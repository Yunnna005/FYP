import Card from "../componenets/Card";

export default function Login() {
    return <>
    <div className="hero min-h-screen bg-gradient-to-r from-[#dfe2fe] via-[#b1cbfa] to-[#8e98f5]" >
    <div className="hero-content text-base-content text-center p-10 bg-base-100 rounded-lg shadow-lg">
        <div className="max-w-md">
        <h1 className="mb-1 text-5xl font-bold">Expenses Tracker</h1>
        <p className="mb-10">
            AI-powered expenses tracker with banking API integration
        </p>
        <Card title="Connect your card" description="Track your expenses easily and securely." buttonText="Connect"></Card>
        </div>
    </div>
    </div>;
    </>
}