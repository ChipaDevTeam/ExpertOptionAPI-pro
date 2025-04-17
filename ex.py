import asyncio
import logging
from Expert.api import ExpertOptionAPI
from Expert.indicators import AlligatorIndicator, RSIIndicator

# Configure logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    # Initialize API client
    token = "6c4bbfd4640b9b46ee145650e331b030"  # Replace with new token if necessary
    api = ExpertOptionAPI(token=token, demo=True, server_region="wss://fr24g1us.expertoption.finance/ws/v40")
    
    try:
        # Connect to the server
        await api.connect()
        
        # Fetch and print balance
        balance = api.get_balance()
        print(f"Account balance: {balance}")
        
    except ValueError as e:
        print(f"Error: {str(e)}")
        api.logger.error(f"Main execution failed: {str(e)}", exc_info=True)
    except Exception as e:
        print(f"Error: {str(e)}")
        api.logger.error(f"Main execution failed: {str(e)}", exc_info=True)
    finally:
        await api.disconnect()

if __name__ == "__main__":
    asyncio.run(main())