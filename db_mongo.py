from pymongo import MongoClient

def get_mongo_client():
    # Thay đổi thông tin đăng nhập bên dưới cho phù hợp với MongoDB của bạn
    uri = "mongodb://admin:AdminVpsx@103.214.8.89:27017/gmail_accounts?authSource=admin"
    return MongoClient(uri)

def save_account_to_mongo(account_info):
    client = get_mongo_client()
    db = client['gmail_accounts']
    col = db['accounts']
    col.insert_one(account_info)
    client.close()

def get_created_accounts_count():
    client = get_mongo_client()
    db = client['gmail_accounts']
    col = db['accounts']
    count = col.count_documents({})
    client.close()
    return count
