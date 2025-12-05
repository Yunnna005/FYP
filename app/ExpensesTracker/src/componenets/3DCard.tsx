interface ThreeDCardProps {
    bankName: string;
    cardNumber: string;
    cardHolder: string;
    expiryDate: string;
}


export default function ThreeDCard({bankName, cardNumber, cardHolder, expiryDate}: ThreeDCardProps) {
    return (<>
        <a href="#" className="hover-3d my-12 mx-2 cursor-pointer">
        
        <div className="card w-96 bg-black text-white bg-[radial-gradient(circle_at_bottom_left,#ffffff04_35%,transparent_36%),radial-gradient(circle_at_top_right,#ffffff04_35%,transparent_36%)] bg-size-[4.95em_4.95em]">
            <div className="card-body">
            <div className="flex justify-between mb-10">
                <div className="font-bold">{bankName}</div>
            </div>
            <div className="text-lg mb-4 opacity-40">{cardNumber}</div>
            <div className="flex justify-between">
                <div>
                <div className="text-xs opacity-20">CARD HOLDER</div>
                <div>{cardHolder}</div>
                </div>
                <div>
                <div className="text-xs opacity-20">EXPIRES</div>
                <div>{expiryDate}</div>
                </div>
            </div>
            </div>
        </div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        </a>
        </>
    );
}