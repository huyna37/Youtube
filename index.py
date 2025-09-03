import argparse
from youtube_actions import create_gmail_account, browse_youtube_with_profile
from db_mongo import save_account_to_mongo, get_created_accounts_count


def main():
    parser = argparse.ArgumentParser(description="Gmail Account Creator & Youtube Simulator")
    parser.add_argument("--n", type=int, help="Số lượng tài khoản cần tạo", required=True)
    args = parser.parse_args()

    num_accounts = args.n
    created_count = get_created_accounts_count()
    for i in range(created_count, created_count + num_accounts):
        profile_path = f"profiles/profile_{i+1}/"
        account_info = create_gmail_account(profile_path)
        if account_info:
            save_account_to_mongo(account_info)
            browse_youtube_with_profile(profile_path)
        else:
            print(f"Không thể tạo tài khoản thứ {i+1}")

if __name__ == "__main__":
    main()