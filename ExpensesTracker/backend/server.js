import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { Configuration, PlaidApi, PlaidEnvironments } from "plaid";

dotenv.config();

const app = express();
app.use(cors());
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

app.post("/link/token/create", async (req, res) => {
  try {
    const response = await client.linkTokenCreate({
      user: { client_user_id: "userTest" },
      client_name: "Your App",
      products: ["transactions", "identity"],
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

app.post("/item/public_token/exchange", async (req, res) => {
  const { public_token } = req.body;
  
  const response = await client.itemPublicTokenExchange({ public_token });
  ACCESS_TOKEN = response.data.access_token;
  
  console.log("Stored access token:", ACCESS_TOKEN);

  res.json({ access_token: ACCESS_TOKEN });
});

app.get("/accounts", async (req, res) => {
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

app.get("/identity", async (req, res) => {
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


app.listen(8000, () => console.log("Server running on 8000"));
