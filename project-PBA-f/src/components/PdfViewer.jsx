import { useCallback, useEffect, useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import getFileUrl from "../utils/getFileUrl"
import worker from "pdfjs-dist/build/pdf.worker?url";
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import { useResizeObserver } from '@wojtekmaj/react-hooks';

pdfjs.GlobalWorkerOptions.workerSrc = worker;

export default function PdfViewer({ file }) {
    const [page, setPage] = useState(1);
    const [pageNum, setPageNum] = useState(1);
    const [containerRef,setContainerRef] = useState(null);
    const [containerWidth,setContainerWidth] = useState(null);

    const onResize = useCallback((entires)=>{
        const [entry] = entires;
        if(entry){
            setContainerWidth(entry.contentRect.width);
        }
    },[]);

    useResizeObserver(containerRef,{},onResize);
    
    const onLoadSuccess = ({ numPages }) => {
        setPageNum(numPages);
    };

    const fileUrl = getFileUrl(file);

    function goBack(){
        setPage((cur)=>Math.max(cur-1,1));
    }
    function goNext(){
        setPage((cur)=>Math.min(cur+1,pageNum));
    }
    useEffect(()=>{
        setPage(1);
        setPageNum(1);
    },[file]);

    return (
        <div ref={setContainerRef}>
            <h2 style={{height:"100px", alignContent:"center", margin:"0"}}>원본 pdf (비교용)</h2>
            <Document file={fileUrl} onLoadSuccess={onLoadSuccess}>
                <Page pageNumber={page} width={containerWidth} />
            </Document>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', margin: '20px 0',"justifyContent":"center" }}>
                <button onClick={goBack} disabled={page <= 1}>
                    이전
                </button>
                <span>
                    {page} / {pageNum}
                </span>
                <button onClick={goNext} disabled={page >= pageNum}>
                    다음
                </button>
            </div>
        </div>
    );
}