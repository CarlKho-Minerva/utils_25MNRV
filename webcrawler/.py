{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "ename": "RuntimeError",
     "evalue": "asyncio.run() cannot be called from a running event loop",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31mRuntimeError\u001b[0m                              Traceback (most recent call last)",
      "Cell \u001b[0;32mIn[1], line 14\u001b[0m\n\u001b[1;32m     10\u001b[0m         \u001b[38;5;28mprint\u001b[39m(result\u001b[38;5;241m.\u001b[39mmarkdown)\n\u001b[1;32m     13\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;18m__name__\u001b[39m \u001b[38;5;241m==\u001b[39m \u001b[38;5;124m\"\u001b[39m\u001b[38;5;124m__main__\u001b[39m\u001b[38;5;124m\"\u001b[39m:\n\u001b[0;32m---> 14\u001b[0m     \u001b[43masyncio\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mrun\u001b[49m\u001b[43m(\u001b[49m\u001b[43mmain\u001b[49m\u001b[43m(\u001b[49m\u001b[43m)\u001b[49m\u001b[43m)\u001b[49m\n",
      "File \u001b[0;32m/opt/homebrew/Cellar/python@3.11/3.11.11/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/runners.py:186\u001b[0m, in \u001b[0;36mrun\u001b[0;34m(main, debug)\u001b[0m\n\u001b[1;32m    161\u001b[0m \u001b[38;5;250m\u001b[39m\u001b[38;5;124;03m\"\"\"Execute the coroutine and return the result.\u001b[39;00m\n\u001b[1;32m    162\u001b[0m \n\u001b[1;32m    163\u001b[0m \u001b[38;5;124;03mThis function runs the passed coroutine, taking care of\u001b[39;00m\n\u001b[0;32m   (...)\u001b[0m\n\u001b[1;32m    182\u001b[0m \u001b[38;5;124;03m    asyncio.run(main())\u001b[39;00m\n\u001b[1;32m    183\u001b[0m \u001b[38;5;124;03m\"\"\"\u001b[39;00m\n\u001b[1;32m    184\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m events\u001b[38;5;241m.\u001b[39m_get_running_loop() \u001b[38;5;129;01mis\u001b[39;00m \u001b[38;5;129;01mnot\u001b[39;00m \u001b[38;5;28;01mNone\u001b[39;00m:\n\u001b[1;32m    185\u001b[0m     \u001b[38;5;66;03m# fail fast with short traceback\u001b[39;00m\n\u001b[0;32m--> 186\u001b[0m     \u001b[38;5;28;01mraise\u001b[39;00m \u001b[38;5;167;01mRuntimeError\u001b[39;00m(\n\u001b[1;32m    187\u001b[0m         \u001b[38;5;124m\"\u001b[39m\u001b[38;5;124masyncio.run() cannot be called from a running event loop\u001b[39m\u001b[38;5;124m\"\u001b[39m)\n\u001b[1;32m    189\u001b[0m \u001b[38;5;28;01mwith\u001b[39;00m Runner(debug\u001b[38;5;241m=\u001b[39mdebug) \u001b[38;5;28;01mas\u001b[39;00m runner:\n\u001b[1;32m    190\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m runner\u001b[38;5;241m.\u001b[39mrun(main)\n",
      "\u001b[0;31mRuntimeError\u001b[0m: asyncio.run() cannot be called from a running event loop"
     ]
    }
   ],
   "source": [
    "import asyncio\n",
    "from crawl4ai import *\n",
    "\n",
    "\n",
    "async def main():\n",
    "    async with AsyncWebCrawler() as crawler:\n",
    "        result = await crawler.arun(\n",
    "            url=\"https://www.nbcnews.com/business\",\n",
    "        )\n",
    "        print(result.markdown)\n",
    "\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    asyncio.run(main())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
