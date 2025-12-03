interface CardProps {
    title: string;
    description: string;
    buttonText: string;
}

export default function Card({ title, description, buttonText }: CardProps){
    return <div className="card card-border bg-base-200 w-96">
  <div className="card-body items-center text-center">
    <h2 className="card-title">{title}</h2>
    <p>{description}</p>
    <div className="card-actions justify-center">
      <button className="btn btn-outline btn-info">{buttonText}</button>
    </div>
  </div>
</div>
}