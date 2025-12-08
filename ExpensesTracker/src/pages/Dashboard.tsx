/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import Template from "../templates/Template";

export default function Dashboard() {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [identity, setIdentity] = useState([]);

    useEffect(() => {
    async function loadData() {
        try {
            const accRes = await fetch("http://localhost:8000/accounts");
            const accData = await accRes.json();
            setAccounts(accData.accounts || []);

            const idRes = await fetch("http://localhost:8000/identity");
            const idData = await idRes.json();
            setIdentity(idData.identity || []);

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
                            <div className="mb-10 bg-white shadow-lg p-6 rounded-lg">
                                <h2 className="text-xl font-bold mb-1">Account Details</h2>
                                {accounts?.length > 0 ? (
                                    <>
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

                            <div className="mb-10 bg-white shadow-lg p-6 rounded-lg">
                                <h2 className="text-xl font-bold mb-1">Identity Details</h2>

                    {identity.length > 0 ? (
                        identity.map((acc: any) => (
                            <div key={acc.account_id} className="mb-4 p-4 border rounded-lg">
                                {acc.owners?.map((owner: any, i: number) => (
                                    <div key={i} className="mt-3">
                                        <p><strong>Full Name:</strong> {owner.names?.join(", ")}</p>
                                        <p><strong>Emails:</strong> {owner.emails?.map((e: { data: any; }) => e.data).join(", ")}</p>
                                        <p><strong>Phone Numbers:</strong> {owner.phone_numbers?.map((p: { data: any; }) => p.data).join(", ")}</p>
                                        <p><strong>Addresses:</strong></p>
                                        {owner.addresses?.map((a: any, j: number) => (
                                            <div key={j} className="ml-4">
                                                <p>{a.data.street} {a.data.city} {a.data.region}</p>
                                                <p>{a.data.postal_code}</p>
                                            </div>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        ))
                    ) : (
                        <p>No identity information found</p>
                    )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </Template>
    );
}
