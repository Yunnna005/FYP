import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { Configuration, PlaidApi, PlaidEnvironments } from "plaid";
import {getTransactionsByOwner} from "./db/db_utils.js";
import {getUserByEmailAndPhone} from "./db/db_utils.js";
import {getMonthlyStatsByUserId} from "./db/db_utils.js";
 
dotenv.config();

const app = express();
app.use(cors({
  origin: "http://localhost:3000",
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type"],
  credentials: true
}));
app.use(express.json());

let ACCESS_TOKEN = null;

const config = new Configuration({
  basePath: PlaidEnvironments.sandbox,
  baseOptions: {
    headers: {
      "PLAID-CLIENT-ID": process.env.PLAID_CLIENT_ID,
      "PLAID-SECRET": process.env.PLAID_SECRET,
    },
  },
});
const client = new PlaidApi(config);

app.post("/api/link/token/create", async (req, res) => {
  try {
    const response = await client.linkTokenCreate({
      user: { client_user_id: "userTest" },
      client_name: "Your App",
      products: ["auth", "identity"],
      language: "en",
      redirect_uri: null,
      country_codes: ["US"],
    });
    console.log("Link token response:", response.data);
    res.json(response.data);
  } catch (error) {
    console.error("Plaid error:", error.response?.data || error);
    res.status(500).json({ error: "Failed to create link token" });
  }
});

app.post("/api/item/public_token/exchange", async (req, res) => {
  const { public_token } = req.body;
  
  const response = await client.itemPublicTokenExchange({ public_token });
  ACCESS_TOKEN = response.data.access_token;
  
  console.log("Stored access token:", ACCESS_TOKEN);

  res.json({ access_token: ACCESS_TOKEN });
});

app.get("/api/auth", async (req, res) => {
  try {
    if (!ACCESS_TOKEN) {
      return res.status(400).json({ error: "No access token saved" });
    }

    const response = await client.authGet({
      access_token: ACCESS_TOKEN,
    });

    const accountNumber = response.data.numbers.ach.map(item => item.account) || [];

    res.json({ accountNumber });
  } catch (error) {
    console.error("Error fetching auth data:", error.response?.data || error);
    res.status(500).json({ error: "Failed to fetch auth data" });
  }
});

//Get account info (type, subtype, starting_balance, currency, meta: name, official_name, mask)
app.get("/api/accounts", async (req, res) => {
  try {
    if (!ACCESS_TOKEN) {
      return res.status(400).json({ error: "No access token saved" });
    }

    const response = await client.accountsGet({
      access_token: ACCESS_TOKEN,
    });

    res.json({ accounts: response.data.accounts });
  } catch (error) {
    console.error("Error fetching accounts:", error.response?.data);
    res.status(500).json({ error: "Failed to fetch accounts" });
  }
});

//Get identity info (names, phone numbers, emails, addresses)
app.get("/api/identity", async (req, res) => {
  try {
    if (!ACCESS_TOKEN) {
      return res.status(400).json({ error: "No access token saved" });
    }

    const response = await client.identityGet({
      access_token: ACCESS_TOKEN,
    });

    res.json({ identity: response.data.accounts });
  } catch (error) {
    console.error("Error fetching identity:", error.response?.data || error);
    res.status(500).json({ error: "Failed to fetch identity" });
  }
});

app.get("/api/identity/login", async (req, res) => {
  try{
    if(!ACCESS_TOKEN){
      return res.status(400).json({ error: "No access token saved" });
    }

    const response = await client.identityGet({
      access_token: ACCESS_TOKEN,
    })
    const identityData = response.data.accounts || [];
    const firstOwner = identityData[0]?.owners?.[0];

    const email = firstOwner?.emails?.[0]?.data || "";
    const phone = firstOwner?.phone_numbers?.[0]?.data || "";

    res.json({ email, phone });
  }catch (error){
    console.error("Error fetching identity:", error.response?.data || error);
    res.status(500).json({ error: "Failed to fetch identity" });
  }
})

app.get("/api/account/user", async (req, res) => {
  const { email, phone } = req.query;

  if (!email || !phone) return res.status(400).json({ error: "Email and phone are required" });

  try {
    const user = await getUserByEmailAndPhone(email, phone);
    
    if (!user) return res.status(404).json({ error: "User not found" });

    res.json(user);
  } catch (err) {
    console.error("Error fetching user:", err);
    res.status(500).json({ error: "Failed to fetch user" });
  }
})

app.get("/api/account/transactions", async (req, res) => {
  const { email, phone } = req.query;

  if (!email || !phone) {
    return res.status(400).json({ error: "Email and phone are required" });
  }

  try {
    const transactions = await getTransactionsByOwner(email, phone);
    res.json({ transactions });
  } catch (err) {
    console.error("Error in /api/transactions/owner:", err);
    res.status(500).json({ error: "Failed to fetch transactions" });
  }
});

app.get("/app/account/monthly_stats", async (req, res) => {
  const {user_id} = req.query;
  const {account_number} = req.query;

  if (!user_id) {
    return res.status(400).json({ error: "User ID is required" });
  }

  try {
    const stats = await getMonthlyStatsByUserId(user_id, account_number);
    res.json({ stats });
  } catch (err) {
    console.error("Error in /api/account/monthly_stats:", err);
    res.status(500).json({ error: "Failed to fetch monthly stats" });
  }
});


app.listen(8000, () => console.log("Server running on 8000"));
