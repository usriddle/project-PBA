export default function ModeBtn({btnName,callback,mode,condition}){
    return(<>
        <button style={{"width":"100px",margin:"10px"}} onClick={()=>{callback(mode)}} disabled={condition}>{btnName}</button>
    </>)
}