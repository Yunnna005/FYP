export default function NavBar() {
    return <ul className="menu bg-base-200 rounded-box w-auto h-screen fixed top-0 left-0 p-4 gap-4">
        <p className="text-2xl font-bold p-4">Expenses Tracker</p>
        <li className="text-lg"><a>Dashboard</a></li>
        <li className="text-lg"><a>Chat</a></li>
    </ul>;
}