'''
Created on 24-Nov-2025

@author: Praveensavanth.N
'''

if __name__ == '__main__':
    pass

'''
Created on 21-Nov-2025
@author: Praveensavanth.N
'''

import time
import requests
import json
from collections import defaultdict
import urllib3
urllib3.disable_warnings()


def get_csrf_token(session, service_root_url, username, password):
    headers = {
        "x-csrf-token": "Fetch",
        "Accept": "application/json"
    }
    print("🔍 Fetching CSRF Token from SAP Gateway...")
    response = session.get(service_root_url, headers=headers, auth=(username, password), verify=False)

    if response.status_code == 200:
        csrf_token = response.headers.get("x-csrf-token")
        if not csrf_token:
            raise Exception("❌ CSRF Token not found in response headers!")
        print("✅ CSRF Token fetched successfully")
        return csrf_token
    else:
        raise Exception(f"❌ Failed to fetch CSRF Token. Status: {response.status_code}, Response: {response.text}")


def update_record(session, update_url, csrf_token, payload):
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("📤 Calling OData PATCH to update SAP record...")
    response = session.put(update_url, headers=headers, json=payload, verify=False)
    return response

# ------------------------------------------------------------
# 1. READ DATA FROM SAP ODATA SERVICE
# ------------------------------------------------------------

# OData service URL
url = "https://vhdtbps4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/ItEInvDataSet?$format=json"
#url = "https://vhdtbqs4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/ItEInvDataSet?$format=json"
# Credentials
#username = "PRAVEENS"
#password = "Bunty@123s4567892"
#username = "PS4_ADMIN"
#password = "7890@$Cloudstar$54234"
username = "DA_E_INV"
password = "Dibs@da123"

try:
    response = requests.get(
        url,
        auth=(username, password),
        headers={"Accept": "application/json"},
        verify=False
    )

    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("Error fetching OData:", response.text)
        exit()

    sap_json = response.json()

except Exception as e:
    print("Exception occurred:", str(e))
    exit()

sap_data = sap_json["d"]["results"]

# ------------------------------------------------------------
# 2. GROUP SAP DATA BY VBELN (Multiple invoices)
# ------------------------------------------------------------

invoices = defaultdict(list)

for row in sap_data:
    vbeln = row.get("Vbeln")
    invoices[vbeln].append(row)

print(f"Total invoices detected: {len(invoices)}")


# Service root URL used only for CSRF fetch (no key predicate)
#SERVICE_ROOT = "https://vhdtbqs4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/"
SERVICE_ROOT = "https://vhdtbps4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/"

# Actual Update URL containing composite keys
#UPDATE_URL = "https://vhdtbqs4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/ItEInvDataSet(Kunnr='1',Vbeln='4002')"
UPDATE_URL = "https://vhdtbps4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/ItEInvDataSet(Kunnr='1',Vbeln='4002')"

session = requests.Session()

try:
    # STEP 1 → Fetch CSRF token
    csrf_token = get_csrf_token(session, SERVICE_ROOT, username, password)
    #print("CSRF Token", csrf_token )
    #time.sleep(10)
except Exception as e:
    print("🔥 Exception:", str(e))    

# ------------------------------------------------------------
# 3. LOOP THROUGH EACH VBELN AND POST TO ONFACT
# ------------------------------------------------------------

#onfact_url = "https://uat-api5.onfact.be/v1/invoices.json"
#API_KEY = "%riov0ssurzbuc0#qxso2q1xspoltk&1%nadv18%h85ichl6xyawi5h3k3m%fhik"
#uuid = "616f714d-ff9c-41aa-8423-cf42c285c00a"

onfact_url = "https://api5.onfact.be/v1/invoices.json"
API_KEY = "&sjx!drxsgv7c6volu9#e4lamw5li2fskiklztot&%&nf2985dw%26p0yg02zz#x"
uuid = "48d9454d-803c-4ea9-a9a5-7755b9c893e1"


onfact_headers = {
    "X-ACTIONS": "FIND-OR-CREATE-CUSTOMER,FIND-PRODUCTS,USE-FIRST-DESCRIPTION,USE-FIRST-TOPTEXT-DESCRIPTION",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-SESSION-KEY": API_KEY,
    "X-Company-Uuid": uuid
     }


for vbeln, items in invoices.items():

    print("\n----------------------------------------")
    print(f"Preparing invoice for VBELN: {vbeln}")
    print("----------------------------------------")

    first = items[0]   # header level values
    
    # Variable holding your VBELN number
    w_vbeln = first.get("Vbeln", 0)   # replace with your dynamic value

    # Build the OData service URL dynamically
    #url = f"https://vhdtbqs4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INV_PDF_BASE64_SRV/ZDA_E_INV_PDF_BASE64Set(IVbeln='{w_vbeln}')?$format=json"
    url = f"https://vhdtbps4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INV_PDF_BASE64_SRV/ZDA_E_INV_PDF_BASE64Set(IVbeln='{w_vbeln}')?$format=json"
    
    # Authentication (replace with your SAP credentials)
    #auth = ("PRAVEENS", "Bunty@123s4567892")
    #auth = ("PS4_ADMIN", "7890@$Cloudstar$54234")
    auth = ("DA_E_INV", "Dibs@da123")

    # Call the OData service
    response = requests.get(
        url,
        auth=(username, password),
        headers={"Accept": "application/json"},
        verify=False
    )
    ebas64_value = ''
    if response.status_code == 200:
        data = response.json()
    # Extract the EBas64 field
        ebas64_value = data.get("d", {}).get("EBas64")
        print("EBas64 field value:", ebas64_value)
    else:
        print("Error:", response.status_code, response.text)

    number = int(first.get("Vbeln", 0))
    last_8_digits = str(number)[-8:]
    
    if first.get("Cat", "") == 'CRN': 
        #onfact_url = "https://uat-api5.onfact.be//v1/creditnotes.json"
        onfact_url = "https://api5.onfact.be//v1/creditnotes.json"
        invoice_payload = {
            "date": first.get("InvDate", ""),
            "customer_name": first.get("Name", ""),
            "currency_id": first.get("Waers", "USD"),
            "order_reference": int(first.get("Vbeln", 0)),
            "term": int(first.get("TermDays", 0)),
            "exchange_rate": float(first.get("ExRate", 1)),
            "customer_vat": first.get("VatNo", ""),
            "external_pdf": ebas64_value,
            "number": last_8_digits,
            "creditnote_lines": []
        }
        for row in items:    
            line = {
                "quantity": float(row.get("Qty", 0)),
                "name": row.get("Matnr", ""),
                "price": float(row.get("Rate", 0)),
                "vat": float(row.get("VatPer", 0))
            }
            invoice_payload["creditnote_lines"].append(line)
        
    else:
        #onfact_url = "https://uat-api5.onfact.be/v1/invoices.json"
        onfact_url = "https://api5.onfact.be/v1/invoices.json"
        invoice_payload = {
            "date": first.get("InvDate") or "",
            "customer_name": first.get("Name") or "",
            "currency_id": first.get("Waers") or "USD",
            "order_reference": int(first.get("Vbeln") or 0),
            "term": int(first.get("TermDays") or 0),
            "exchange_rate": float(first.get("ExRate") or 1.0),
            "customer_vat": first.get("VatNo") or "",
            "external_pdf": ebas64_value,
            "number": last_8_digits,
            "invoice_lines": []
         # Add line items for this VBELN only
        }
        for row in items:
            line = {
                "quantity": float(row.get("Qty", 0)),
                "name": row.get("Matnr", ""),
                "price": float(row.get("Rate", 0)),
                "vat": float(row.get("VatPer", 0))
            }
            invoice_payload["invoice_lines"].append(line)
    

    print("Invoice payload:")
    print(json.dumps(invoice_payload, indent=4))

    print("Sending invoice to OnFact...")

    onfact_response = requests.post(
        onfact_url,
        headers=onfact_headers,
        data=json.dumps(invoice_payload)
    )
    # -------------------------------------------------------
    # PEPPOL - Send invoice to Peppol after OnFact posting
    # -------------------------------------------------------

    # Extract OnFact invoice ID from response
    iddata = json.loads(onfact_response.text)
    onfact_invoice_id = str(iddata.get("id", ""))

    # Build Peppol URL using the OnFact invoice ID
    peppol_url = f"https://api5.onfact.be/v1/invoices/{onfact_invoice_id}/peppol.json"

    # Peppol payload - identifier taken dynamically from VatNo
    peppol_payload = {
    "identifier": first.get("VatNo", ""),
    "scheme": "BE:VAT"
    }

    print(f"📡 Sending to Peppol URL: {peppol_url}")

    # Post to Peppol
    onfact_peppol = requests.post(
        peppol_url,
        headers=onfact_headers,
        data=json.dumps(peppol_payload)
    )

    print("Peppol Status Code:", onfact_peppol.status_code)
    print("Peppol Response:", onfact_peppol.text)

    # Extract first 8 characters of Peppol response ID
    peppol_data = json.loads(onfact_peppol.text)
    peppol_response_id = str(peppol_data.get("id", ""))
    peppol_id_first8 = peppol_response_id[:8]

    print(f"✅ Peppol ID (first 8 chars): {peppol_id_first8}")

    print("Status Code:", onfact_response.status_code)
    print("OnFact Response:", onfact_response.text)
    # 🔥 IMPORTANT: Add delay to avoid 429 error
    # Prepare PATCH payload → remove __metadata, send only actual fields
    iddata = json.loads(onfact_response.text)
    onfact_id = iddata.get("id")
    patch_payload =      {
    #"d": {
    #"__metadata": {
    #  "id": "https://vhdtbqs4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/ItEInvDataSet(Kunnr='1',Vbeln='4002')",
    #  "uri": "https://vhdtbqs4ci.sap.dimexon.com:44300/sap/opu/odata/SAP/ZDA_E_INVOICE_PROCESS_SRV/ItEInvDataSet(Kunnr='1',Vbeln='4002')",
    #  "type": "ZDA_E_INVOICE_PROCESS_SRV.ItEInvData"
    #},
    #    "Mandt": "100",
        "PeppolId": peppol_id_first8,
    #    "Posnr":first.get("Posnr", 0),
    #    "VatPer": first.get("VatPer", 0),
    #    "Cat": first.get("Cat", ""),
    #    "Kunnr": first.get("Kunnr", ""),
        "Vbeln": first.get("Vbeln", 0),
    #    "InvDate": first.get("InvDate", ""),
    #    "Name": first.get("Name", ""),
    #    "VatNo": first.get("VatNo", ""),
    #    "TermDays": first.get("TermDays", 0),
    #    "ExRate": first.get("ExRate", 0),
    #    "Waers": first.get("Waers", "USD"),
    #    "Qty": first.get("Qty", 0),
    #    "Matnr": first.get("Matnr", ""),
    #    "Rate": first.get("Rate", 0),
    #    "Value": first.get("Value", 0),
        "RetId": str(iddata.get("id",""))
    #}
    }
        
    
    try:
        print(json.dumps(patch_payload, indent=4))
        
        # STEP 2 → Call PATCH update
        update_response = update_record(session, UPDATE_URL, csrf_token, patch_payload)

        print("🔎 HTTP Status Code:", update_response.status_code)
        print("📥 Response:", update_response.text)

        if update_response.status_code in [200, 204]:
            print("🎉 Record updated successfully in")
        else:
            print("⚠ Update failed — possible key format or payload issue!")
            print("Gateway Error:", update_response.text)
        
    except Exception as e:
            print("🔥 Exception:", str(e))
    
    time.sleep(10)

