import { useEffect, useState } from "react";

export default function getFileUrl(file){
    const [fileUrl, setFileUrl] = useState("");
    useEffect(()=>{
    const url = URL.createObjectURL(file);
    setFileUrl(url)
    return ()=>{
        URL.revokeObjectURL(url)
    }
    },[file]);
    return fileUrl;
}