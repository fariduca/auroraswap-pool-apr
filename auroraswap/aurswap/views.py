from asyncio.windows_events import NULL
import itertools
from pprint import pprint
from django.shortcuts import render
from django.http import HttpResponse
from web3 import Web3
import json, requests, copy

w3 = Web3(Web3.HTTPProvider('https://mainnet.aurora.dev'))

#Contract abi and address
BRL_CHEF_ABI = json.loads('''[{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"address","name":"_BRL","internalType":"contract BRLToken"},{"type":"address","name":"_devaddr","internalType":"address"},{"type":"address","name":"_feeAddress","internalType":"address"},{"type":"uint256","name":"_BRLPerBlock","internalType":"uint256"},{"type":"uint256","name":"_startBlock","internalType":"uint256"}]},{"type":"event","name":"Deposit","inputs":[{"type":"address","name":"user","internalType":"address","indexed":true},{"type":"uint256","name":"pid","internalType":"uint256","indexed":true},{"type":"uint256","name":"amount","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"event","name":"EmergencyWithdraw","inputs":[{"type":"address","name":"user","internalType":"address","indexed":true},{"type":"uint256","name":"pid","internalType":"uint256","indexed":true},{"type":"uint256","name":"amount","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"event","name":"OwnershipTransferred","inputs":[{"type":"address","name":"previousOwner","internalType":"address","indexed":true},{"type":"address","name":"newOwner","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"Withdraw","inputs":[{"type":"address","name":"user","internalType":"address","indexed":true},{"type":"uint256","name":"pid","internalType":"uint256","indexed":true},{"type":"uint256","name":"amount","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"BONUS_MULTIPLIER","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"contract BRLToken"}],"name":"BRL","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"BRLPerBlock","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"add","inputs":[{"type":"uint256","name":"_allocPoint","internalType":"uint256"},{"type":"address","name":"_lpToken","internalType":"contract IBEP20"},{"type":"uint16","name":"_depositFeeBP","internalType":"uint16"},{"type":"bool","name":"_withUpdate","internalType":"bool"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"deposit","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"uint256","name":"_amount","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"dev","inputs":[{"type":"address","name":"_devaddr","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"devaddr","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"emergencyWithdraw","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"feeAddress","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"getMultiplier","inputs":[{"type":"uint256","name":"_from","internalType":"uint256"},{"type":"uint256","name":"_to","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"massUpdatePools","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"owner","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"pendingBRL","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"address","name":"_user","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"lpToken","internalType":"contract IBEP20"},{"type":"uint256","name":"allocPoint","internalType":"uint256"},{"type":"uint256","name":"lastRewardBlock","internalType":"uint256"},{"type":"uint256","name":"accBRLPerShare","internalType":"uint256"},{"type":"uint16","name":"depositFeeBP","internalType":"uint16"}],"name":"poolInfo","inputs":[{"type":"uint256","name":"","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"poolLength","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"renounceOwnership","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"set","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"uint256","name":"_allocPoint","internalType":"uint256"},{"type":"uint16","name":"_depositFeeBP","internalType":"uint16"},{"type":"bool","name":"_withUpdate","internalType":"bool"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setFeeAddress","inputs":[{"type":"address","name":"_feeAddress","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"startBlock","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"totalAllocPoint","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"transferOwnership","inputs":[{"type":"address","name":"newOwner","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"updateEmissionRate","inputs":[{"type":"uint256","name":"_BRLPerBlock","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"updatePool","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"amount","internalType":"uint256"},{"type":"uint256","name":"rewardDebt","internalType":"uint256"}],"name":"userInfo","inputs":[{"type":"uint256","name":"","internalType":"uint256"},{"type":"address","name":"","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"withdraw","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"uint256","name":"_amount","internalType":"uint256"}]}]''')
BRL_CHEF_ADDR = w3.toChecksumAddress('0x35CC71888DBb9FfB777337324a4A60fdBAA19DDE')

#Creating a BRL_CHEF contract
chefContract = w3.eth.contract(address=BRL_CHEF_ADDR, abi=BRL_CHEF_ABI)

#Other abi's
UNI_ABI = json.loads('''[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"sync","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]''')
ERC20_ABI = json.loads('''[{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"string","name":"name_","internalType":"string"},{"type":"string","name":"symbol_","internalType":"string"}]},{"type":"event","name":"Approval","inputs":[{"type":"address","name":"owner","internalType":"address","indexed":true},{"type":"address","name":"spender","internalType":"address","indexed":true},{"type":"uint256","name":"value","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"event","name":"Transfer","inputs":[{"type":"address","name":"from","internalType":"address","indexed":true},{"type":"address","name":"to","internalType":"address","indexed":true},{"type":"uint256","name":"value","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"allowance","inputs":[{"type":"address","name":"owner","internalType":"address"},{"type":"address","name":"spender","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"approve","inputs":[{"type":"address","name":"spender","internalType":"address"},{"type":"uint256","name":"amount","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"balanceOf","inputs":[{"type":"address","name":"account","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint8","name":"","internalType":"uint8"}],"name":"decimals","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"decreaseAllowance","inputs":[{"type":"address","name":"spender","internalType":"address"},{"type":"uint256","name":"subtractedValue","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"increaseAllowance","inputs":[{"type":"address","name":"spender","internalType":"address"},{"type":"uint256","name":"addedValue","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"string","name":"","internalType":"string"}],"name":"name","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"string","name":"","internalType":"string"}],"name":"symbol","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"totalSupply","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"transfer","inputs":[{"type":"address","name":"recipient","internalType":"address"},{"type":"uint256","name":"amount","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"transferFrom","inputs":[{"type":"address","name":"sender","internalType":"address"},{"type":"address","name":"recipient","internalType":"address"},{"type":"uint256","name":"amount","internalType":"uint256"}]}]''')

AuroraTokens = [
    { "id": "weth", "symbol": "WETH", "contract": "0xC9BdeEd33CD01541e1eeD10f90519d2C06Fe3feB"},
    { "id": "wrapped-near", "symbol": "WNEAR", "contract": "0xC42C30aC6Cc15faC9bD938618BcaA1a1FaE8501d"},
    { "id": "polaris-token", "symbol": "PLRS", "contract": "0xD93d770C123a419D4c48206F201Ed755dEa3037B"},
    { "id": "terra-luna", "symbol": "LUNA", "contract": "0xC4bdd27c33ec7daa6fcfd8532ddB524Bf4038096"},
    { "id": "frax", "symbol": "FRAX", "contract": "0xDA2585430fEf327aD8ee44Af8F1f989a2A91A3d2"},
    { "id": "rose", "symbol": "ROSE", "contract": "0xdcd6d4e2b3e1d1e1e6fa8c21c8a323dcbecff970"},
    { "id": "nearpad", "symbol": "PAD", "contract": "0x885f8CF6E45bdd3fdcDc644efdcd0AC93880c781"},
    { "id": "usd-coin", "symbol": "USDC", "contract": "0xb12bfca5a55806aaf64e99521918a4bf0fc40802"},
    { "id": "dai", "symbol": "DAI", "contract": "0xe3520349f477a5f6eb06107066048508498a291b"},
    { "id": "dai", "symbol": "DAI", "contract": "0x53810e4c71bc89d39df76754c069680b26b20c3d"},
    { "id": "terrausd", "symbol": "UST", "contract": "0x5ce9F0B6AFb36135b5ddBF11705cEB65E634A9dC"},
    { "id": "mimatic", "symbol": "MIMATIC", "contract": "0xdFA46478F9e5EA86d57387849598dbFB2e964b02"}
]

def getErc20Prices(prices, poolToken):
    price = prices[poolToken['address']]['usd'] if poolToken['address'] in prices.keys() else None
    tvl = poolToken['totalSupply'] * price / 10 ** poolToken['decimals']
    staked_tvl = poolToken['staked'] * price
    poolUrl=f'https://aurorascan.dev/address/{poolToken["address"]}'

    return dict(
        staked_tvl= staked_tvl,
        price= price,
        stakeTokenTicker= poolToken['symbol'],
        tvl= tvl
    )
    
    

def getUniPrices(tokens, prices, poolToken):
    
    # print('=======================')
    # pprint(poolToken)
    # print('=======================')
    # pprint(tokens)
    # print('=======================')
    # pprint(prices)
    # print('=======================')

    t0 = tokens[poolToken['token0']]
    p0 = prices[poolToken['token0']]['usd'] if poolToken['token0'] in prices.keys() else None
    t1 = tokens[poolToken['token1']]
    p1 = prices[poolToken['token1']]['usd'] if poolToken['token1'] in prices.keys() else None

    if p0 is None and p1 is None:
        print(f'Missing prices for tokens {poolToken["token0"]} and {poolToken["token1"]}.')
        return None

    if t0 is not None and t0['decimals'] is None:
        print(f'Missing information for token {poolToken["token0"]}.')
        return None
    
    if t1 is not None and t1['decimals'] is None:
        print(f'Missing information for token {poolToken["token1"]}.')
        return None
    
    q0 = poolToken['q0'] / 10 ** t0['decimals']
    q1 = poolToken['q1'] / 10 ** t1['decimals']
    if p0 is None:
        p0 = q1 * p1 / q0
        prices[poolToken["token0"]] = { "usd" : p0 }
    
    if p1 is None:
        p1 = q0 * p0 / q1
        prices[poolToken["token1"]] = { "usd" : p1 };    

    tvl = q0 * p0 + q1 * p1
    price = tvl / poolToken['totalSupply']
    prices[poolToken['address']] = { 'usd' : price }
    staked_tvl = poolToken['staked'] * price
    stakeTokenTicker = f'[{t0["symbol"]}]-[{t1["symbol"]}]'

    return dict(
        t0= t0,
        p0= p0,
        q0= q0,
        t1= t1,
        p1= p1,
        q1= q1,
        price= price,
        tvl= tvl,
        staked_tvl= staked_tvl,
        stakeTokenTicker= stakeTokenTicker
    )

def getPoolPrices(tokens, prices, poolInfos):
    poolPrices=[]

    for i, poolInfo in enumerate(poolInfos):
        if i != 0:
            poolToken = poolInfo['poolToken']
            if 'token0' in poolToken.keys():
                poolPrices.append(getUniPrices(tokens, prices, poolToken))
            else:
                poolPrices.append(getErc20Prices(prices, poolToken))

    return poolPrices

def lookUpPrices(id_array):
    prices = {}
    ids = '%2C'.join(id_array)
    res = requests.get(url='https://api.coingecko.com/api/v3/simple/price?ids=' + ids + '&vs_currencies=usd')

    for key, v in res.json().items():
        if (v['usd']):
            prices[key] = v
      
    return prices

def getAuroraPrices():
    idPrices = lookUpPrices(list(map(lambda x: x['id'], AuroraTokens)))
    prices = {}
    for bt in AuroraTokens:
        if (idPrices[bt['id']]):
            prices[bt['contract']] = idPrices[bt['id']]
    return prices


def getAuroraUniPool(pool, poolAddress):
    decimals = pool.functions.decimals().call() 
    token0 = pool.functions.token0().call()
    token1 = pool.functions.token1().call()
    symbol = pool.functions.symbol().call()
    name = pool.functions.name().call()
    totalSupply = pool.functions.totalSupply().call()
    staked = pool.functions.balanceOf(BRL_CHEF_ADDR).call()
    #unstaked = pool.functions.balanceOf(App.YOUR_ADDRESS).call()
    
    q0 = 0
    q1 = 0
    is1inch = True
    try:
        reserves = pool.functions.getReserves().call()
        # print('\n')
        # print(poolAddress)
        # print('\n')
        # print(reserves)        
        q0 = reserves[0]
        q1 = reserves[1]
        is1inch = False
    except:       
        if (token0 == "0x0000000000000000000000000000000000000000"):
            q0 = w3.eth.getBalance(poolAddress)
        else:
            c0 = w3.eth.contract(address=token0, abi=ERC20_ABI)
            q0 = c0.functions.balanceOf(poolAddress).call()
        
        if (token1 == "0x0000000000000000000000000000000000000000"):
            q1 = w3.eth.getBalance(poolAddress)
        else:
            c1 = w3.eth.contract(address=token1, abi=ERC20_ABI)
            q1 = c1.functions.balanceOf(poolAddress).call()

        is1inch = True
    return dict(
        symbol=symbol,
        name=name,
        address=poolAddress,
        token0=token0,
        q0=q0,
        token1=token1,
        q1=q1,
        totalSupply= totalSupply / 10 ** decimals,
        stakingAddress= BRL_CHEF_ADDR,
        staked= staked / 10 ** decimals,
        decimals= decimals,
        #unstaked= unstaked / 10 ** decimals,
        contract= pool,
        tokens = [token0, token1],
        is1inch=is1inch
    )

def getAuroraErc20(token, address):
    decimals = token.functions.decimals().call()
    staked = token.functions.balanceOf(BRL_CHEF_ADDR).call()
    #unstaked = token.functions.balanceOf(App.YOUR_ADDRESS).call()
    name = token.functions.name().call()
    symbol= token.functions.symbol().call()
    totalSupply= token.functions.totalSupply().call()
    return dict(
        address=address,
        name=name,
        symbol=symbol,
        totalSupply=totalSupply,
        decimals=decimals,
        staked=staked / 10 ** decimals,
        #unstaked: unstaked  / 10 ** decimals,
        contract= token,
        tokens=[address]
    )


def getAuroraToken(tokenAddress):

    try:
        pool = w3.eth.contract(address=tokenAddress, abi=UNI_ABI)
        #const _token0 = await App.ethcallProvider.all([pool.token0()]);
        uniPool = getAuroraUniPool(pool, tokenAddress)
        #window.localStorage.setItem(tokenAddress, "uniswap");
        # print('\n')
        # print(uniPool)        

        return uniPool
    except:
        pass
    try:
        erc20 = w3.eth.contract(address=tokenAddress, abi=ERC20_ABI)
        #_name = await App.ethcallProvider.all([erc20.name()]);
        erc20tok = getAuroraErc20(erc20, tokenAddress)
        #window.localStorage.setItem(tokenAddress, "erc20")
        # print('\n')
        # print(erc20tok)

        return erc20tok
    except:
        print('Exception occured')


def getPoolInfos():
    poolIndexes = [0,1,14]
    # poolIndexes = [0]
    poolInfos = []

    for i in poolIndexes:
        poolInfo = chefContract.functions.poolInfo(i).call() # => [lpToken(address) allocPoint(uint256) lastRewardBlock(uint256) accBRLPerShare(uint256) depositFeeBP(uint16)]                
        poolToken = getAuroraToken(poolInfo[0])
        poolInfos.append(dict
        (            
            address= poolInfo[0],
            allocPoints= poolInfo[1],
            poolToken= poolToken
            # userStaked= staked,
            # pendingRewardTokens= pendingRewardTokens / 10 ** 18,
            # depositFee= (poolInfo.depositFeeBP ?? 0) / 100,
            # withdrawFee= (poolInfo.withdrawFeeBP ?? 0) / 100
        ))
    
    return poolInfos


def read_pool_data():    

    poolCount = chefContract.functions.poolLength().call()
    totalAllocPoints = chefContract.functions.totalAllocPoint().call()
    rewardTokenAddress = chefContract.functions.BRL().call()

    pc_dict = { 'varName' : 'poolCount', 'varValue' : poolCount }    
    tap_dict = { 'varName' : 'totalAllocPoints', 'varValue' : totalAllocPoints }
    rta_dict = { 'varName' : 'rewardTokenAddress', 'varValue' : rewardTokenAddress }

    current_block = w3.eth.get_block_number()
    multiplier = chefContract.functions.getMultiplier(current_block, current_block+1).call()
    rewardsPerWeek = chefContract.functions.BRLPerBlock().call() /1e18 * multiplier * 604800 / 1.1 
    
    cb_dict = { 'varName' : 'currentBlock', 'varValue' : current_block}
    mul_dict = { 'varName' : 'multiplier', 'varValue' :  multiplier }
    rpw_dict = { 'varName' : 'rewardsPerWeek', 'varValue' : rewardsPerWeek }

    #Getting desired pools infos
    poolInfos = getPoolInfos()
    #Token addrs from pools infos
    tokenAddresses = list(set(itertools.chain(*list(map(lambda x: x['poolToken']['tokens'], poolInfos)))))
    # print('\n')
    # print(tokenAddresses)

    tokens = {}
    for t_a in tokenAddresses:
        exists = list(filter(lambda x: x['address'] == t_a, poolInfos))
        if (len(exists) > 0):
            tokens[t_a] = copy.copy(exists[0]['poolToken'])
        else:
            tokens[t_a] = getAuroraToken(t_a)

    #Get aurora tokens prices
    prices = getAuroraPrices()
    # print('\n')
    # print(prices)

    #Get poolPrices for the pools in poolInfo
    poolPrices = getPoolPrices(tokens, prices, poolInfos)

    poolRewardsPerWeek = poolInfos[1]['allocPoints'] / totalAllocPoints * rewardsPerWeek
    rewardPrice = prices[rewardTokenAddress]['usd']
    staked_tvl = poolPrices[0]['staked_tvl']

    usdPerWeek = poolRewardsPerWeek * rewardPrice
    weeklyAPR = usdPerWeek / staked_tvl * 100
    yearlyAPR = weeklyAPR * 52

    res = {"tokenTicker": poolPrices[0]['stakeTokenTicker'], "YearlyAPR": "{0:.2f}".format(yearlyAPR)}

    return res


def getPoolAPR(request):
    res = read_pool_data()    
    context = {
        "res": res
    }
    return render(request, 'aurswap.html', context) 



def index(request):
    return render(request, 'aurswap.html')
