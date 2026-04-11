import NavBar from "../componenets/NavBar";


export default function Template({ children }: { children: React.ReactNode }) {
    return (
        <div className="drawer lg:drawer-open">
            <input id="app-drawer" type="checkbox" className="drawer-toggle" />

            <div className="drawer-content flex flex-col">  
                <div className="navbar bg-sky-950 text-slate-200 lg:hidden">
                    <label htmlFor="app-drawer" aria-label="open sidebar" className="btn btn-square btn-ghost">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block h-6 w-6 stroke-current">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </label>
                    <span className="text-xl font-bold px-2">Expenses Tracker</span>
                </div>

                {/* Page content */}
                <div>{children}</div>
            </div>

            <div className="drawer-side">
                <label htmlFor="app-drawer" aria-label="close sidebar" className="drawer-overlay"></label>
                <NavBar />
            </div>
        </div>
    );
}