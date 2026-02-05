interface Transaction {
  date: Date; 
  description: string;
  amount: number;
  currency_code: string;
  pending: boolean;
}

type TableProps = {
  transactions: Transaction[];
};

export default function Table({ transactions }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="table table-zebra w-full">
        <thead>
          <tr>
            <th>#</th>
            <th>Merchant</th>
            <th>Date</th>
            <th>Amount</th>
            <th>Currency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
            {transactions.length > 0 ? (
                transactions.map((tx, index) => (
                <tr key={index}>
                    <th>{index + 1}</th>
                    <td>{tx.description}</td>
                    <td>{new Date(tx.date).toLocaleDateString()}</td>
                    <td>€{Number(tx.amount).toFixed(2)}</td>
                    <td>{tx.currency_code}</td>
                    <td>{tx.pending ? "Pending" : "Completed"}</td>
                </tr>
                ))
            ) : (
                <tr>
                <td colSpan={6} className="text-center">
                    No transactions found.
                </td>
                </tr>
            )}
        </tbody>
      </table>
    </div>
  );
}
