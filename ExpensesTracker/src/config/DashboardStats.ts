export interface DashboardStat {
  title: string;
  field: string;
  desc: string;
}

export const DashboardStats: DashboardStat[] = [
  {
    title: "Total Income",
    field: "total_received",
    desc: "All credited transactions",
  },
  {
    title: "Total Spent",
    field: "total_spent",
    desc: "All debited transactions",
  },
  {
    title: "Transactions",
    field: "total_transactions",
    desc: "Total transactions on record",
  },
  {
    title: "Avg. Transaction",
    field: "avg_transaction",
    desc: "Mean value across all transactions",
  },
  {
    title: "Largest Transaction",
    field: "largest_abs",
    desc: "Biggest single transaction this month",
  },
  { title: "Net Cashflow", 
    field: "net_cashflow", 
    desc: "Received minus spent" 
  }
];