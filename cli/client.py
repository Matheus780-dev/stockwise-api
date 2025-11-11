import argparse
import getpass
import requests
import json

API = "http://127.0.0.1:8000"


def register():
    username = input("username: ")
    password = getpass.getpass("password: ")
    r = requests.post(
        f"{API}/users/", params={"username": username, "password": password})
    print(r.status_code, r.text)


def login():
    username = input("username: ")
    password = getpass.getpass("password: ")
    r = requests.post(
        f"{API}/token", data={"username": username, "password": password})
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("Token:", token)
        return token
    else:
        print("Login failed:", r.status_code, r.text)
        return None


def create_product(token):
    name = input("name: ")
    price = float(input("price: "))
    qty = int(input("quantity: "))
    category = input("category (optional): ")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{API}/products/", params={"name": name, "price": price,
                      "quantity": qty, "category": category or None},
                      headers=headers)
    print(r.status_code, r.text)


def list_products(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API}/products/", headers=headers)
    print(json.dumps(r.json(), indent=2, default=str))


def make_sale(token):
    pid = int(input("product_id: "))
    qty = int(input("quantity: "))
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{API}/sales/", params={"product_id": pid, "quantity": qty},
        headers=headers)
    print(r.status_code, r.text)


def get_report_csv(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API}/reports/sales/csv", headers=headers)
    print(r.status_code, r.text)


def get_report_pdf(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API}/reports/sales/pdf", headers=headers)
    print(r.status_code, r.text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=[
                        "register", "login", "create_product",
                        "list_products", "sale", "report_csv", "report_pdf"])
    args = parser.parse_args()
    if args.cmd == "register":
        register()
    elif args.cmd == "login":
        t = login()
        if t:
            print("Save this token to use other commands.")
    else:
        token = input("token: ")
        if args.cmd == "create_product":
            create_product(token)
        elif args.cmd == "list_products":
            list_products(token)
        elif args.cmd == "sale":
            make_sale(token)
        elif args.cmd == "report_csv":
            get_report_csv(token)
        elif args.cmd == "report_pdf":
            get_report_pdf(token)


if __name__ == "__main__":
    main()
