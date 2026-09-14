import {useState } from "react";
import FileSelector from "../components/FileSelector";
import SummaryViewer from "../components/SummaryViewer";
import ImageViewer from "../components/ImageViewer"
import { requestSummary } from "../api/requestSummary";
import PdfViewer from "../components/PdfViewer";
import axios from "axios"
import downloadSummary from "../utils/downloadSummary";

export const ALLOW_IMAGE_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp"
];

export function MainPage(){
    const [file, setFile] = useState(null);
    const [content, setContent] = useState("요약할 문서를 업로드해주세요.");
    const [status, setStatus] = useState(0);
    const [wait, setWait] = useState(0);
    const [duration, setDuration] = useState(0);

    // 1. 타이머와 대기 시간을 함께 관리하는 함수
    function increaseWait(startTime) {
        const waitInterval = setInterval(() => {
            const currentWait = Math.floor((Date.now() - startTime) / 1000);
            setWait(currentWait);
        }, 1000);

        return waitInterval;
    }

    async function requestUpload(){
        const startTime = Date.now(); // 요청 시작 시간 기록
        const waitInterval = increaseWait(startTime);
        
        try {
            setContent(`파일 유효성 검사 통과, 로딩중...`);
            setStatus(1);
            const response = await requestSummary(file);
            if(!response.data || !response.data.summary){
                throw new Error("서버 데이터 응답 형식이 올바르지 않습니다.")
            }

            // 성공한 경우
            const responseSummary = response.data.summary;
            downloadSummary(responseSummary, file.name);
            setContent(responseSummary);
            setStatus(2);
        } catch (error) {
            setStatus(3);
            if(axios.isAxiosError(error)){
                if(error.response){
                    const statusCode = error.response.status;
                    if(statusCode == 400){
                        setContent("잘못된 요청입니다.");
                    }
                    else if(statusCode == 401 || statusCode == 403){
                        setContent("권한이 없습니다.");
                    }
                    else if(statusCode >= 500){
                        setContent("서버 내부 오류입니다. 관리자에게 문의해주세요.");
                    }
                    else{
                        setContent("요청에 실패했습니다.");
                    }
                }
                else if(error.request){
                    setContent("요청을 보냈으나, 서버로부터 응답을 받지 못했습니다.");
                }
            }
            else{
                setContent("알 수 없는 오류가 발생했습니다.");
            }
        }
        finally{
            clearInterval(waitInterval);
            // 2. 최종 소요 시간 계산 (초 단위)
            const finalDuration = Math.floor((Date.now() - startTime) / 1000);
            setDuration(finalDuration);
            setWait(0);
        }
    }
    
    return(
        <div style={{"textAlign":"center", 
        "display":"flex",
        "flexDirection":"column", 
        "alignItems":"center",
        "gap":"10px"}}>
            <h1>문서 요약 시스템</h1>
            <div>
                <FileSelector setFile={setFile} setContent={setContent} setStatus={setStatus}/>
                {file && <button style={{"width":"70px"}} onClick={requestUpload} disabled={file && status==1}>요약 시작</button>}
            </div>
            {status==2 && <><h3>소요 시간: {duration}초</h3><h2>요약결과</h2></>}
            {status==1 && <h3>대기시간: {wait}초</h3>}
            <SummaryViewer content={content}/>
            {file && file.type == "application/pdf" && <PdfViewer file={file}/>}
            {file && ALLOW_IMAGE_TYPES.includes(file.type) && <ImageViewer file={file}/>}
        </div>
    )
}