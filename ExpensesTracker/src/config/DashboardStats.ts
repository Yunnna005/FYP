export interface DashboardStat {
  title: string;
  field: string;
  desc: string;
  format?: (v: number) => string;
}

export const DashboardStats: DashboardStat[] = [
  {
    title: "Total Income",
    field: "total_receive",
    desc: "All credited transactions",
    format: (v: number) => `$${v.toFixed(2)}`,
  },
  {
    title: "Total Spent",
    field: "total_spend",
    desc: "All debited transactions",
    format: (v: number) => `$${v.toFixed(2)}`,
  },
  {
    title: "Transactions",
    field: "total_transactions",
    desc: "Total transactions on record",
  },
  {
    title: "Avg. Transaction",
    field: "avg_transaction_value",
    desc: "Mean value across all transactions",
    format: (v: number) => `$${v.toFixed(2)}`,
  },
  {
    title: "Largest Transaction",
    field: "largest_abs",
    desc: "Biggest single transaction this month",
    format: (v: number) => `$${v.toFixed(2)}`,
  },
];