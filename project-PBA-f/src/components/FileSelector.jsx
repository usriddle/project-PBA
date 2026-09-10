export default function FileSelector({ onSelect }) {
  return (
    <input
      type="file"
      accept="application/pdf"
      onChange={(event) => onSelect(event.target.files?.[0] ?? null)}
    />
  );
}
