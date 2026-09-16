import ModeBtn from "./ModeBtn";
import "../assets/css/button.css";
import { useState } from "react";

export default function SummaryViewer({result,requestUpload,status,openHook}) {
  const [open,setOpen] = openHook;
  function summaryCallback(){
    return {requestUpload, setOpen};
  }

  return (
    <div style={{height:"100%"}}> 
      <div width="100%" style={{display:"flex", height:"100px", justifyContent:"space-around"}}>
        <button disabled={status==1} onClick={()=>{status!=1 && setOpen(true)}} style={{flex:"1", borderRadius:"5px 0 0 5px", borderRight:"0"}} className={`button button--winona button--border-thin button--round-s ${open &&"selected-color"}`}>요약 메뉴</button>
        <button onClick={()=>{setOpen(false)}}style={{flex:"1", borderRadius:"0 5px 5px 0"}} className={`button button--winona button--border-thin button--round-s ${!open &&"selected-color"}`}>요약 결과</button>
      </div>
        {open ? <div style={{display:"flex",flexDirection:"column",justifyContent:"space-between"}}>
                    <ModeBtn btnName={"일반 요약 시작"} callback={summaryCallback} mode={"main"} condition={status==1}/>
                    <ModeBtn btnName={"짧은 요약 시작"} callback={summaryCallback} mode={"short"} condition={status==1}/>
                    <ModeBtn btnName={"쉬운 요약 시작"} callback={summaryCallback} mode={"kid"} condition={status==1}/>
                    <ModeBtn btnName={"영어 요약 시작"} callback={summaryCallback} mode={"en"} condition={status==1}/>
                    <ModeBtn btnName={"청크 요약 시작"} callback={summaryCallback} mode={"chunk"} condition={status==1}/>
                </div>:
                <div style={{height:"100%", display:"flex"}}>
                  <div style={{width:"100%",
                      height:"70%",
                      whiteSpace: "pre-wrap",     // 개행과 공백을 유지하면서 자동 줄바꿈
                      wordBreak: "break-word", // 긴 단어가 영역을 넘지 않도록 강제 줄바꿈
                      padding:"20px",
                      borderRadius:"5px",
                      border:"1px solid black"
                    }}>
                    {result}
                  </div>
                </div>
        }        
    </div>
  );
}
