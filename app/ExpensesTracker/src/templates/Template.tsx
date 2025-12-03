import NavBar from "../componenets/NavBar";

export default function Template({ children }: { children: React.ReactNode }) {
    return <div>
    <NavBar />  
        <div className="ml-64">
            {children}
        </div>  
    </div>;
}