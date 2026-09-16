import {useState } from "react";
import FileSelector from "../components/FileSelector";
import SummaryViewer from "../components/SummaryViewer";
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
    const [result, setResult] = useState("요약 대기중... \n다른 작업을 원하시면 일단 취소 버튼을 눌러주세요.");
    //코드 / 0:기본 / 1: 업로드 후 대기 / 2: 요약 성공 /3: 오류 /4:취소
    const [status, setStatus] = useState(0);
    const [wait, setWait] = useState(0);
    const [duration, setDuration] = useState(0);
    const [curInterval,setCurInteval] =useState(null);
    const [open,setOpen] =useState(true)

    const controller = new AbortController();
    const signal = controller.signal;


    function increaseWait(){
        const waitInterval = setInterval(()=>{
            setWait((cur)=>(cur+1));
        },1000)

        return waitInterval
    }

    async function requestUpload(mode="main"){
        const startTime = Date.now(); // 요청 시작 시간 기록
        const waitInterval = increaseWait(startTime);
        setCurInteval(waitInterval);

        
        try {
            setContent(`파일 유효성 검사 통과, 요약 종류를 선택하세요.`);
            setStatus(1);
            const response = await requestSummary(file,mode,signal);
            if(!response.data || !response.data.summary){
                //error를 발생시켜 catch 문에서 오류 메시지 처리
                throw new Error("서버 데이터 응답 형식이 올바르지 않습니다.")
            }

            // 성공한 경우
            const responseSummary = response.data.summary;
            downloadSummary(responseSummary, file.name);
            setResult(responseSummary);
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
            setCurInteval(null);
            // 2. 최종 소요 시간 계산 (초 단위)
            const finalDuration = Math.floor((Date.now() - startTime) / 1000);
            setDuration(finalDuration);
            setWait(0);
            clearInterval(waitInterval);
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
                <FileSelector setFile={setFile} setContent={setContent} statusHook={[status, setStatus]}/>
                <button onClick={()=>{
                    controller.abort();
                    setStatus(4);
                    clearInterval(curInterval);
                    setCurInteval(null);
                    setWait(0);
                    setOpen(true);
                }} style={{float:"right", width:"50px", height:"30px"}} className="button button--winona button--border-thin button--round-s">취소</button>
            </div>
            {status==2 && <><h3>소요 시간: {duration}초</h3><h2>요약결과</h2></>}
            {status==1 && <h3>대기시간: {wait}초</h3>}
            <h4>{content}</h4>
            <div style={{display:"flex", width:"100%"}}>
                <div style={{width:"50%"}}>
                    {file && file.type == "application/pdf" && <PdfViewer file={file}/>}
                    {file && ALLOW_IMAGE_TYPES.includes(file.type) && <ImageViewer file={file}/>}
                </div>
                <div style={{width:"50%"}}>
                    {file && <SummaryViewer result={result} requestUpload={requestUpload} status={status} openHook={[open,setOpen]}/>}
                </div>
            </div>
        </div>
        )
}