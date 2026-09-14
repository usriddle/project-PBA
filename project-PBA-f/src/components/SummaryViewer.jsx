export default function SummaryViewer({content}) {
  return (
    <div  style={{display:"flex",justifyContent:"space-around"}}>
      <div style={{width:"600px",
        whiteSpace: "pre-wrap",     // 개행과 공백을 유지하면서 자동 줄바꿈
          wordBreak: "break-word"      // 긴 단어가 영역을 넘지 않도록 강제 줄바꿈
      }}>
        {content}
      </div>
    </div>
  );
}
