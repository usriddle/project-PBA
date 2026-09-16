import getFileUrl from "../utils/getFileUrl";

export default function ImageViewer({file}){
    const imageUrl = getFileUrl(file);
    return <div>
        <img src={imageUrl} 
        style={{maxWidth: "100%",  
                height: "auto",
                objectFit: "cover" }}/>
    </div>
}