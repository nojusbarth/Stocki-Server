# copyright (c) Dr. Oliver Barth 2021

from collections import OrderedDict

STOCKI_STOCKNAMES = OrderedDict([
    ('DAX PERFORMANCE-INDEX', '^GDAXI'), #-------------------- indices
    ('TECDAX PR', '^TECDAX'),
    ('Dow Jones Industrial Average', '^DJI'),
    ('NASDAQ Composite', '^IXIC'),
    ('iShares Core MSCI World UCITS ETF USD (Acc)', 'IWDA.L'), #-------------------- iShares
    ('iShares Dow Jones Global Titans 50 UCITS ETF (DE)', 'EXI2.DE'),
    ('iShares Dow Jones U.S. Select Dividend UCITS ETF (DE)', 'EXX5.DE'),
    ('iShares STOXX Global Select Dividend 100 UCITS ETF (DE)', 'ISPA.DE'),
    ('iShares Edge MSCI World Momentum Factor UCITS ETF USD (Acc)', 'IS3R.DE'),
    ('iShares Global Water UCITS ETF USD (Dist)', 'IQQQ.DE'),
    ('iShares MSCI Europe Quality Dividend UCITS ETF EUR', 'QDVX.DE'),
    ('iShares Core High Dividend ETF', 'HDV'),
    ('Invesco S&P 500 High Dividend Low Volatility ETF', 'SPHD'),
    ('SPDR S&P Global Dividend ETF','WDIV'),         
    ('iShares Automation & Robotics UCITS ETF', '2B76.DE'),
    ('iShares Oil & Gas Exploration & Production UCITS ETF USD', 'IS0D.DE'),
    ('Brent Crude Oil Last Day Finance', 'BZ=F'), #-------------------- mat
    ('Gold', 'GC=F'),
    ('EUWAX Gold', 'GOLD.SG'),
    ('Platinum','PL=F'),
    ('Copper', 'HG=F'),
    ('Aluminum Futures', 'ALI=F'),
    ('Barrick Gold Corporation', 'GOLD'),
    ('BHP Group', 'BHP'), # materials
    ('Jiangxi Copper Company Limited', '0358.HK'),
    ('Zijin Mining Group Company Limited', '2899.HK'),
    ('China Rare Earth Holdings Limited', '0769.HK'),
    ('Lynas Rare Earths Limited', 'LYSCF'),
    ('BHP Group Limited', 'BHP.AX'), #-------------------- high yield
    ('Enagas S.A.', 'ENG.MC'),
    ('Medical Properties Trust Inc.', 'MPW'),
    ('Norsk Hydro ASA', 'NHY.OL'),
    ('Pioneer Natural Resources Company', 'PXD'),
    ('Rio Tinto Group', 'RIO.L'),
    ('Bitcoin USD', 'BTC-USD'), #-------------------- krypto
    ('Ethereum USD', 'ETH-USD'),
    ('adidas AG', 'ADS.DE'), #-------------------- dax
    ('Airbus SE', 'AIR.PA'),
    ('Allianz SE', 'ALV.DE'),
    ('BASF SE', 'BAS.DE'),
    ('Bayer Aktiengesellschaft', 'BAYN.DE'),
    ('BMW Aktiengesellschaft', 'BMW.DE'),
    ('Brenntag SE', 'BNR.DE'),
    ('Continental Aktiengesellschaft', 'CON.DE'),
    ('Covestro AG', '1COV.DE'),
    ('Daimler Truck Holding AG', 'DTG.DE'),
    ('Delivery Hero SE', 'DHER.DE'),
    ('Deutsche Bank AG', 'DBK.DE'),
    ('Deutsche Boerse AG', 'DB1.DE'),
    ('Deutsche Post AG', 'DHL.DE'),
    ('Deutsche Telekom AG', 'DTE.DE'),
    ('E.ON SE', 'EOAN.DE'),
    ('Fresenius SE & Co. KGaA', 'FRE.DE'),
    ('Fresenius Medical Care AG & Co. KGaA', 'FMS'),
    ('Hannover Rueck SE', 'HNR1.DE'),
    ('HeidelbergCement AG', 'HEI.DE'),
    ('HelloFresh SE', 'HFG.DE'),
    ('Henkel AG & Co. KGaA', 'HEN3.DE'),
    ('Infineon Technologies AG', 'IFX.DE'),
    ('Linde plc', 'LIN.DE'),
    ('Mercedes-Benz Group AG', 'MBG.DE'),
    ('Merck & Co., Inc.', 'MRK'),
    ('MTU Aero Engines AG', 'MTX.DE'),
    ('Muenchener Rueck', 'MUV2.DE'),
    ('Porsche Automobil Holding SE', 'PAH3.DE'),
    ('PUMA SE', 'PUM.DE'),
    ('QIAGEN N.V.', 'QIA.DE'),
    ('RWE AG', 'RWE.DE'),
    ('SAP SE', 'SAP.DE'),
    ('Sartorius Aktiengesellschaft', 'SRT.DE'),
    ('Siemens Aktiengesellschaft', 'SIE.DE'),
    ('Siemens Healthineers AG', 'SHL.SG'),
    ('Symrise AG', 'SY1.DE'),
    ('Volkswagen AG', 'VOW.DE'),
    ('Vonovia SE', 'VNA.DE'),
    ('Zalando SE', 'ZAL.DE'),
    ('Deutsche Lufthansa AG', 'LHA.DE'),
    ('Siemens Energy AG', 'ENR.DE'),
    ('1&1 AG', '1U1.DE'), #-------------------- tecdax
    ('AIXTRON SE', 'AIXA.DE'),
    ('Bechtle AG', 'BC8.DE'),
    ('CompuGroup Medical SE & Co. KGaA', 'COP.DE'),
    ('DWS Group GmbH & Co. KGaA', 'DWS.DE'),
    ('freenet AG', 'FNTN.DE'),
    ('Nemetschek SE', 'NEM.DE'),
    ('MorphoSys AG', 'MOR.DE'),
    ('Pfeiffer Vacuum Technology AG', 'PFV.DE'),
    ('Telefonica Deutschland Holding AG', 'O2D.DE'),
    ('Aurubis AG', 'NDA.DE'), #-------------------- mdax
    ('Commerzbank AG', 'CBK.DE'),
    ('Knorr-Bremse Aktiengesellschaft', 'KBX.DE'),
    ('ProSiebenSat.1 Media SE', 'PSM.DE'),
    ('Software Aktiengesellschaft', 'SOW.DE'),
    ('TAG Immobilien AG', 'TEG.DE'),
    ('thyssenkrupp AG', 'TKA.DE'),
    ('Wacker Chemie AG', 'WCH.DE'),
    ('United Internet AG', 'UTDI.DE'),
    ('ASML Holding N.V.', 'ASME.DE'), #-------------------- XETRA
    ('3M Company', 'MMM'), #-------------------- dow jones
    ('Altria Group Inc.', 'MO'),
    ('Amgen Inc.','AMGN'), 
    ('Biogen Inc.', 'BIIB'),
    ('Gilead Sciences Inc.', 'GILD'),
    ('Apple Inc.', 'AAPL'), #-------------------- NASDAQ
    ('BioMarin Pharmaceutical Inc.', 'BMRN'),
    ('The Coca-Cola Company', 'KO'),
    ('JD.com, Inc.', 'JD'),
    ('Microsoft Corporation', 'MSFT'),
    ('NVIDIA Corporation', 'NVDA'),
    ('The Procter & Gamble Company', 'PG'),
    ('Verizon Communications Inc.', 'VZ'),
    ('Walmart Inc.', 'WMT'),
    ('Weichai Power Co., Ltd.', '2338.HK'), #-------------------- China
    ('Haier Smart Home Co., Ltd.', '6690.HK'),    
    ('Nel ASA', 'NEL.OL'), # green
    ('Tesla, Inc.', 'TSLA'),       
    ('British American Tobacco p.l.c.', 'BMT.DE'), #-------------------- dividend
    ('LTC Properties, Inc.', 'LTC') ,
    ])

STOCKI_STOCKNAMES_TEST = OrderedDict([
    ('DAX PERFORMANCE-INDEX', '^GDAXI'), # indices
    ('TECDAX PR', '^TECDAX'),
    ('Dow Jones Industrial Average', '^DJI'),
    ])

STOCKI_STOCKNAMES_FAV = OrderedDict()


