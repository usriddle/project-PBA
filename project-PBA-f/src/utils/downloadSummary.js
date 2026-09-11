
export default function downloadSummary(summary,name){
    const blob = new Blob([summary],{type:"text/plain;charset=utf-8"});
    const url = URL.createObjectURL(blob);
    const aLink = document.createElement("a");
    aLink.href = url;
    aLink.download = `${name} 요약.txt`;
    aLink.click();

    URL.revokeObjectURL(url);
}