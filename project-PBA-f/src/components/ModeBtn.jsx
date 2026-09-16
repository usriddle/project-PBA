export default function ModeBtn({btnName,callback,mode,condition}){
    const {requestUpload,setOpen} = callback();
    return(<>
        <button className="button button--winona button--border-thin button--round-s" style={{width:"100%", height:"100px"}} 
            onClick={()=>{
                requestUpload(mode);
                setOpen(false);
            }} disabled={condition}>
                <div>
                    {[...btnName].map((char)=>{
                    return(
                        <span>{char}</span>
                    )
                    })}
                </div>
            </button>
    </>)
}