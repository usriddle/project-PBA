import { validatePdf } from "../utils/validatePdf";

export default function FileSelector({ setFile, setContent,statusHook }) {
  const [status, setStatus] = statusHook;
  return (
    <input
      disabled ={status==1}
      type="file"
      accept="application/pdf"
      onChange={(event) => {
        const file = event.target.files?.[0] ?? null;
        const validateResult = validatePdf(file);
        setContent(validateResult.message);
        if(validateResult.code>0){
            setFile(file);
        }
        else{
          setFile(null);
          setStatus(3);
        }
        
      }}
    />
  );
}
