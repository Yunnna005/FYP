import { useEffect, useState } from "react";
import Template from "../templates/Template";

export default function Dashboard() {
    const [accounts, setAccounts] = useState([]);
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                // Fetch accounts
                const accRes = await fetch("http://localhost:8000/accounts");
                const accData = await accRes.json();
                setAccounts(accData.accounts || []);

                // Fetch transactions
                const txRes = await fetch("http://localhost:8000/transactions");
                const txData = await txRes.json();
                setTransactions(txData.transactions);

                setLoading(false);
            } catch (error) {
                console.error("Error loading Plaid data:", error);
            }
        }

        loadData();
    }, []);

    return (
        <Template>
            <div className="min-h-screen bg-base-200">
                
                {/* Header */}
                <div className="p-2 border-b-2 border-sky-900">
                    <h1 className="text-2xl font-bold text-sky-950 mb-3 mt-3 ml-7">
                        Dashboard
                    </h1>
                </div>

                <div className="p-10 w-auto">
                    {loading ? (
                        <p className="text-lg">Loading your financial data...</p>
                    ) : (
                        <>
                            {/* USER ACCOUNT DETAILS */}
                            <div className="mb-10 bg-white shadow-lg p-6 rounded-lg">
                                <h2 className="text-xl font-bold mb-4">Account Details</h2>
                                
                                
                                {accounts?.length > 0 ? (
                                    <>
                                        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                                        {accounts.map((acc: any) => (
                                            <div key={acc.account_id} className="mb-4 p-4 border rounded-lg">
                                                <p><strong>Name:</strong> {acc.name}</p>
                                                <p><strong>Type:</strong> {acc.type}</p>
                                                <p><strong>Subtype:</strong> {acc.subtype}</p>
                                                <p><strong>Balance:</strong> €{acc.balances.current}</p>
                                            </div>
                                        ))}
                                    </>
                                ) : (
                                    <p>No accounts found</p>
                                )}
                            </div>

                            {/* TRANSACTIONS TABLE */}
                            <div className="bg-white shadow-lg p-6 rounded-lg ">
                                <h2 className="text-xl font-bold mb-4">Recent Transactions</h2>

                                <div className="overflow-x-auto rounded-box border border-base-content/5 bg-base-100">
                                    <table className="table">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Name</th>
                                            <th>Amount</th>
                                            <th>Category</th>
                                        </tr>
                                    </thead>
                                    <tbody>

                                    {transactions?.length > 0 ? (
                                        <>
                                        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                                        {transactions.map((tx: any) => (
                                            <tr key={tx.transaction_id}>
                                                <td>{tx.date}</td>
                                                <td>{tx.name}</td>
                                                <td>€{tx.amount}</td>
                                                <td>{tx.category?.join(", ")}</td>
                                            </tr>
                                            
                                        ))}
                                        </>
                                        ) : (
                                            <tr>
                                                <td colSpan={4}>No transactions found</td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </Template>
    );
}
