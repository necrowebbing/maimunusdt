from aiocryptopay import AioCryptoPay, Networks

cryptopay = AioCryptoPay(token="323803:AAho7IvwmgsoCbfrR8Xzd3oiXlGYFzD2VYP", network=Networks.MAIN_NET)

async def CreateWithdrawCheck(value, tgId) -> str:
    try:
        check = await cryptopay.create_check(
            asset="USDT", 
            amount=value, 
            pin_to_user_id=tgId
        )
        return f"{check.bot_check_url}"
    except Exception as ex:
        return f"OnCheckCreateError:{ex}"
    
async def CreateInvoice(value) -> dict:
    try:
        invoice = await cryptopay.create_invoice(
            asset="USDT",
            amount=value,
            description="Пополнение кассы Meimun USDT"
        )
        return {
            "url": invoice.bot_invoice_url,
            "id": invoice.invoice_id
        }
    except Exception as e:
        print(f"Ошибка создания счета: {e}")
        return {}

async def getBalance(currency_code: str = "USDT"):
    try:
        balances = await cryptopay.get_balance()
        
        for balance_obj in balances:
            if hasattr(balance_obj, 'currency_code') and balance_obj.currency_code == currency_code:
                if hasattr(balance_obj, 'available') and balance_obj.available is not None:
                    return float(balance_obj.available)
        
        print(f"Currency {currency_code} not found in balances")
        return 0.0
        
    except Exception as e:
        print(f"Error getting crypto balance: {type(e).__name__}: {e}")
        return 0.0
