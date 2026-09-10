import { useState } from "react";
import FileSelector from "../components/FileSelector";


export default function MainPage(){
    const [file,setFile] = useState(null);
    
    return(
        <div style={{"textAlign":"center"}}>
            <h1>문서 요약 시스템</h1>
            <br/>
            <FileSelector onselect={setFile}/>
        </div>
        )
}