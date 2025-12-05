// export_plaid_sandbox.js
require('dotenv').config();
const fs = require('fs');
const { PlaidApi, Configuration, PlaidEnvironments } = require('plaid');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const clientConfig = new Configuration({
  basePath: PlaidEnvironments[process.env.PLAID_ENV || 'sandbox'],
  baseOptions: {
    headers: {
      'PLAID-CLIENT-ID': "",
      'PLAID-SECRET': ""
    },
  },
});
const client = new PlaidApi(clientConfig);

// === NEW UTILITY FUNCTION ===
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
// ==========================

// === CONFIG ===
// Sandbox institutions to create items for. Add more sandbox IDs if you wish.
// See Plaid docs for the full list of sandbox institutions.
const SANDBOX_INSTITUTIONS = [
  //'ins_109508', // First Platypus Bank
  //'ins_109509', // First Gingham Credit Union
  'ins_109512', // Houndstooth Bank
  //'ins_109510', no auth, assets and identity
  //'ins_109511',
  //'ins_43',
  //'ins_116834', no identity
  //'ins_117650',
  //'ins_127287',
  //'ins_132241',
  //'ins_117181',
  //'ins_135858',no auth, assets and identity
  'ins_132363',
  'ins_132361',
  //'ins_133402', no longer supported
  'ins_133502',
  'ins_133503'
];

// products to enable on each Item
const PRODUCTS = ['transactions', 'identity']; // 👈 CHANGED: Added 'auth' back!

// number of transactions to fetch per page
const PAGE_SIZE = 100;

// output files
const ACCOUNTS_CSV = 'accounts2.csv';
const TRANSACTIONS_CSV = 'transactions2.csv';
//const IDENTITY_CSV = 'identity.csv';
// const AUTH_CSV = 'auth.csv'; // You might want to add this

// utility: run an async main
(async function main() {
  try {
    const allAccounts = [];
    const allTransactions = [];
    const allIdentityRows = [];
    // const allAuthRows = []; // You might want to uncomment this

    for (const institution_id of SANDBOX_INSTITUTIONS) {
      console.log(`\n--- Creating sandbox public_token for ${institution_id} ---`);

      // Create a public_token in Sandbox for the chosen institution and products
      const createResp = await client.sandboxPublicTokenCreate({
        institution_id,
        initial_products: PRODUCTS,
          options: {
            webhook: 'https://example.com/fake-webhook', // 👈 add this line
          },
        // optional: you can override test username/password with options.override_username/password
      });

      const public_token = createResp.data.public_token;
      console.log('public_token created');

      // Exchange for access_token
      const exchangeResp = await client.itemPublicTokenExchange({ public_token });
      const access_token = exchangeResp.data.access_token;
      console.log('access_token received');

        await client.sandboxItemFireWebhook({
        access_token,
        webhook_code: 'DEFAULT_UPDATE',
        webhook_type: 'TRANSACTIONS',
        //webhook_type: "AUTH",
        //webhook_type: "IDENTITY",
        //webhook_type: "ASSETS"
        });

        console.log('Waiting 5 seconds for Transactions data to become ready...');
        await sleep(5000); // 👈 NEW: Wait for webhook processing

      // ==== Accounts ====
      try {
        const accountsResp = await client.accountsGet({ access_token });
        const accounts = accountsResp.data.accounts || [];
        // add extra metadata: institution_id (and optionally name from response)
        for (const a of accounts) {
          allAccounts.push({
            institution_id,
            account_id: a.account_id,
            name: a.name,
            official_name: a.official_name,
            subtype: a.subtype,
            type: a.type,
            mask: a.mask,
            balances_current: a.balances?.current,
            balances_available: a.balances?.available,
            balances_limit: a.balances?.limit,
            iso_currency_code: a.balances?.iso_currency_code,
          });
        }
        console.log(`  accounts: ${accounts.length}`);
      } catch (err) {
        console.error('  accounts/get error:', err?.response?.data || err.toString());
      }

      // ==== Auth (with product support validation) ====
      try {
        if (PRODUCTS.includes('auth')) {
          const authResp = await client.authGet({ access_token });
          const numbers = authResp.data.numbers || {};
          const authAccounts = authResp.data.accounts || [];
          
          // NOTE: Data processing for auth would go here
          
          console.log(`  auth accounts: ${authAccounts.length} (ACH/EFT/International numbers available)`);

        } else {
          // This block should now be skipped since 'auth' is back in PRODUCTS
          console.log('  auth: Skipped (not in PRODUCTS list).'); 
        }
      } catch (err) {
        // Check for PRODUCT_NOT_SUPPORTED error specifically
        const isProductUnsupported = err?.response?.data?.error_code === 'PRODUCT_NOT_SUPPORTED';

        if (isProductUnsupported) {
          console.log('  auth/get: Product not supported by this institution. Skipping auth.');
        } else {
          console.error('  auth/get unexpected error:', err?.response?.data || err.toString());
        }
      }
      
      // ==== Transactions (paginated) ====
      // Choose a wide date range (sandbox has synthetic recent transactions).
      const endDate = new Date();
      const startDate = new Date();
      startDate.setFullYear(startDate.getFullYear() - 2); // last 2 years

      let offset = 0;
      while (true) {
        try {
          const txResp = await client.transactionsGet({
            access_token,
            start_date: startDate.toISOString().slice(0, 10),
            end_date: endDate.toISOString().slice(0, 10),
            options: { count: PAGE_SIZE, offset }
          });
          const txs = txResp.data.transactions || [];
          console.log(`  fetched transactions: ${txs.length} (offset ${offset})`);
          for (const t of txs) {
            allTransactions.push({
              institution_id,
              account_id: t.account_id,
              transaction_id: t.transaction_id,
              amount: t.amount,
              date: t.date,
              pending: t.pending,
              merchant_name: t.merchant_name,
              name: t.name,
              category: (t.category || []).join('|'),
              transaction_type: t.transaction_type,
              payment_channel: t.payment_channel,
              pending_transaction_id: t.pending_transaction_id || ''
            });
          }
          if (txs.length < PAGE_SIZE) break;
          offset += txs.length;
        } catch (err) {
          console.error('  transactions/get error:', err?.response?.data || err.toString());
          break;
        }
      }

      // ==== Identity ====
      try {
        const idResp = await client.identityGet({ access_token });
        // identity returns 'accounts' array with owners etc - normalize minimal fields
        const identityAccounts = idResp.data.accounts || [];
        for (const ia of identityAccounts) {
          allIdentityRows.push({
            institution_id,
            account_id: ia.account_id,
            owners: JSON.stringify(ia.owners || []),
            names: JSON.stringify(ia.names || []),
            emails: JSON.stringify((ia.owners || []).map(o => o.email || null)),
            phones: JSON.stringify((ia.owners || []).map(o => o.phones || null)),
          });
        }
        console.log(`  identity accounts: ${identityAccounts.length}`);
      } catch (err) {
        // identity may not be available for every institution
        console.error('  identity/get error:', err?.response?.data || err.toString());
      }
    } // end for each institution

    // === Write CSVs ===
    // accounts.csv
    if (allAccounts.length) {
      const accountsCsvWriter = createCsvWriter({
        path: ACCOUNTS_CSV,
        header: Object.keys(allAccounts[0]).map(k => ({ id: k, title: k })),
      });
      await accountsCsvWriter.writeRecords(allAccounts);
      console.log(`\nWrote ${ACCOUNTS_CSV} (${allAccounts.length} rows)`);
    } else console.log('\nNo accounts to write.');

    // transactions.csv
    if (allTransactions.length) {
      const txCsvWriter = createCsvWriter({
        path: TRANSACTIONS_CSV,
        header: Object.keys(allTransactions[0]).map(k => ({ id: k, title: k })),
      });
      await txCsvWriter.writeRecords(allTransactions);
      console.log(`Wrote ${TRANSACTIONS_CSV} (${allTransactions.length} rows)`);
    } else console.log('No transactions to write.');

    // identity.csv
    /*if (allIdentityRows.length) {
      const idCsvWriter = createCsvWriter({
        path: IDENTITY_CSV,
        header: Object.keys(allIdentityRows[0]).map(k => ({ id: k, title: k })),
      });
      await idCsvWriter.writeRecords(allIdentityRows);
      console.log(`Wrote ${IDENTITY_CSV} (${allIdentityRows.length} rows)`);
    } else console.log('No identity rows to write.');
*/
    console.log('\nDone.');
  } catch (err) {
    console.error('Fatal error:', err?.response?.data || err.toString());
  }
})();