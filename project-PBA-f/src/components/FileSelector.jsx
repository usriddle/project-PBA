import { validatePdf } from "../utils/validatePdf";

export default function FileSelector({ setFile, setContent,statusHook }) {
  const [status, setStatus] = statusHook;
  return (
    <input
      disabled ={status==1}
      type="file"
      accept="application/pdf,image/png,image/jpeg,image/jpg,image/webp"
      onChange={(event) => {
        const file = event.target.files?.[0] ?? null;
        const validateResult = validatePdf(file);
        setContent(validateResult.message);
        if(validateResult.code>0){
            setFile(file);
            setStatus(0);
        }
        else{
          setFile(null);
          setStatus(3);
        }
        
      }}
    />
  );
}
