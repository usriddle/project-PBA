export default function SummaryViewer({content}) {
  return (
    <div  style={{"display":"flex","justifyContent":"space-around"}}>
      <div style={{"width":"600px"}}>
        {content}
      </div>
    </div>
  );
}
