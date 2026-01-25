from Backend.Picar.ExcuteDatabase import supabase
from datetime import datetime, timezone


class Transaction:
    @staticmethod
    def create(
        user_id: str,
        amount: int,
        tx_type: str,
        balance_before: int,
        balance_after: int,
        status: str = "SUCCESS",
        note: str | None = None
    ):
        #Tạo 1 giao dịch (DEPOSIT / WITHDRAW)
        return supabase.table("Transaction").insert({
            "UserID": user_id,
            "Type": tx_type,                     # DEPOSIT | WITHDRAW
            "Amount": int(amount),
            "BalanceBefore": int(balance_before),
            "BalanceAfter": int(balance_after),
            "Status": status,
            "Note": note,
            "CreatedAt": datetime.now(timezone.utc).isoformat()
        }).execute()

    @staticmethod
    def get_by_user(user_id: str, limit: int = 50):

        #Lấy lịch sử giao dịch của user
        return (
            supabase.table("Transaction")
            .select("*")
            .eq("UserID", user_id)
            .order("CreatedAt", desc=True)
            .limit(limit)
            .execute()
        )
