import { validatePdf } from "../utils/validatePdf";

export default function FileSelector({ setFile, setContent,setStatus }) {
  return (
    <input
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
