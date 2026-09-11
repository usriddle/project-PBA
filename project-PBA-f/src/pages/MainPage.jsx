import { useState } from "react";
import FileSelector from "../components/FileSelector";
import SummaryViewer from "../components/SummaryViewer";
import { validatePdf } from "../utils/validatePdf";
import { reqeustSummary } from "../api/requestSummary";
import PdfViewer from "../components/PdfViewer";

export function MainPage(){
    const [file,setFile] = useState(null);
    const [content,setContent] = useState("요약할 문서를 업로드해주세요.");
    const [status, setStatus] = useState(0);
    //코드 / 0:기본 / 1: 업로드 후 대기 / 2: 요약 성공 /3: 오류

    async function requestUpload(){
        try {
            setContent("파일 유효성 검사 통과, 로딩중...");
            const response = await reqeustSummary(file);
            setContent(response.data.summary);
            setStatus(2);
        } catch (error) {
            setContent(`${error.name}: ${error.message}`); //디버그용, 추후 변경사항
            setStatus(3);
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
                <FileSelector setFile={setFile} setContent ={setContent} setStatus={setStatus}/>
                {file && <button style={{"width":"70px"}} onClick={requestUpload} disabled ={file && status==1}>요약 시작</button>}
            </div>
            {status==2 && <h2>요약결과</h2>}
            <SummaryViewer content ={content}/>
            {file && <PdfViewer file={file}/>}
        </div>
        )
}