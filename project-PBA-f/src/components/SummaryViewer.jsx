export default function SummaryViewer({content}) {
  return (
    <div  style={{"display":"flex","justifyContent":"space-around"}}>
      <pre style={{"width":"600px"}}>
        {content}
      </pre>
    </div>
  );
}
