import boto3
import os
import sys
import subprocess

def main():
    repo = os.environ.get("REPO_NAME", "").lower()
    new_word = os.environ.get("NEW_WORD", "").lower()
    pr_number = os.environ.get("PR_NUMBER", "")

    if not (repo and new_word and pr_number):
        print("Missing environment variables.")
        sys.exit(1)

    dynamodb = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION"))

    try:
        resp = dynamodb.query(
            TableName="pytori_shiritori",
            KeyConditionExpression="repository_name = :repo",
            ExpressionAttributeValues={":repo": {"S": repo}},
            ScanIndexForward=False,
            Limit=1
        )
    except Exception as e:
        print("🔴 DynamoDB query failed:", e)
        sys.exit(1)

    items = resp.get("Items", [])
    if not items:
        print("🟡 No previous records found. Skipping shiritori check.")
        sys.exit(0)

    prev_word = items[0]["current_word"]["S"].lower()
    expected = new_word[0]
    actual = prev_word[-1]

    if expected != actual:
        msg = f"❌ しりとりエラー：前回の末尾「{actual}」→「{new_word}」は「{expected}」"
        print(msg)
        subprocess.run([
            "gh", "pr", "comment", pr_number,
            "--body", msg
        ])
        sys.exit(1)
    else:
        print(f"✅ OK: しりとり成立（{prev_word} → {new_word}）")

if __name__ == "__main__":
    main()
