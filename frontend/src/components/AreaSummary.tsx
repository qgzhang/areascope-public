interface AreaSummaryProps {
  name: string;
  addressCount: number;
}

function AreaSummary({
  name,
  addressCount,
}: AreaSummaryProps) {
  return (
    <div>
      <h3>{name}</h3>
      <p>{addressCount} addresses</p>
    </div>
  );
}

export default AreaSummary;