import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { Configuration, PlaidApi, PlaidEnvironments } from "plaid";

dotenv.config();

console.log("PLAID_CLIENT_ID:", process.env.PLAID_CLIENT_ID);
console.log("PLAID_SECRET:", process.env.PLAID_SECRET);

const app = express();
app.use(cors());
app.use(express.json());

// Plaid client
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

// Create Link Token
app.post("/link/token/create", async (req, res) => {
  try {
    const response = await client.linkTokenCreate({
      user: { client_user_id: "userTest" },
      client_name: "Your App",
      products: ["transactions", "identity"],
      language: "en",
      webhook: null,
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

// Exchange public_token for access_token
app.post("/item/public_token/exchange", async (req, res) => {
  const { public_token } = req.body;
  const response = await client.itemPublicTokenExchange({ public_token });
  res.json(response.data);
});

app.listen(8000, () => console.log("Server running on 8000"));
