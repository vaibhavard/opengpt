import queue
import os
q = queue.Queue() # create a queue to store the response lines
code_q = queue.Queue() # create a queue to store the response lines

api_endpoint = "https://intagpt.onrender.com/conversation"
nline = False
ans={}
systemp=False
python_boolean_to_json = {
  "true": True,
}
worded=""
stopped=False
about="""                                     
>Graphs
**/mindmap  /flowchart  /complexchart  /linechart  /branchchart /timeline**
"""

up="""<!DOCTYPE html>
<embed src="https://intagpt.up.railway.app/upload" style="width:1000px; height: 500px;">
"""

cont="""<!DOCTYPE html>
<embed src="https://intagpt.up.railway.app/context" style="width:1000px; height: 500px;">
"""

openchat_cookies={'__stripe_mid': 'a7daf6b9-3316-46f3-a1fc-dd2ddf506265a3e407', '_ga': 'GA1.1.563082971.1675761706', '_ga_8Q63TH4CSL': 'GS1.1.1685982627.1.0.1685982627.0.0.0', 'token': 'aqktmuHAPJLKbapaVvLYSRDsmjDHeFTjcGBmqZwdMtcDkfgBPgfUiAITtyAxFocpOBlqhMVxYrHHajtMGXtkVigoIBmfFspmwWDcvwGOJsuxnAmfUWREHjzBBabmyNlR'}
google_cookies={'_ga': 'GA1.3.926487274.1678891938', '_ga_J51Y85KVRZ': 'GS1.1.1678292292.1.1.1678292375.0.0.0', '__utma': '73091649.1747281656.1676968472.1676968472.1676968472.1', '1P_JAR': '2023-10-01-18', 'AEC': 'Ackid1SRUZ_flUxf1yuJGJMTGHKCsTf2ZTRxJq331JLVfyFhCtAXaAy4zV4', 'ANID': 'AHWqTUkJW2WwHfhuE0E0gTjfIu6hGj42qV8_sOqiNqL-2J7QfXHhNvTw3ZHdflN_', 'APISID': 'CGFIrnji7apDtQ-C/ADOYD0j_xPd-ofjJd', 'HSID': 'AbFy40bFgRjYyS0Z5', 'NID': '511=WqchdjwJ7R4ohCxxBsRSjB7ib0qwj7dZERCz1WFPWOcsPE5w0OYs40C_pRl6G2Z000cmHdw8yH8ms6leQ0EKOrTRlLJHwu0ovmJp2aDkaBPHNlMioaeWVqN31coYY3g-ij5js4TKazp0xZb5kSS1ANbtCjiPG8RHn0PWUvmoerEUoDaP4VuFrGiR_IoaEKWgXowcjignUyw_wtBIm6qX8SypPGd8bcWjMIyfilNtgFTJbvU7VJDymrTdFNoOgQEJN9XdydsQ0Id9VlQqWCVZaloIdSAIrBM5Z49iStii8ZHvYC5OYzKvazOoodemrQUpgeg', 'SAPISID': '2BRLvfTlO2VRfGHO/AU0d1fHDmfCYGJfta', 'SEARCH_SAMESITE': 'CgQIrJkB', 'SID': 'bQgdsbc_JRP81SvCAXXEZcip7rq1taCx3fv6xsgVlZsSrpyKQIQfXyRS5oL5Wh6UyWO84w.', 'SIDCC': 'ACA-OxMSa3lTjOR-uchtuEgRjT1s5yYfwCvfqsjQ8SirkWc7rQ--n_g2SxV8Q97legOAcvQA', 'SSID': 'AInRqZh-FT6sG5FNx', '__Secure-1PAPISID': '2BRLvfTlO2VRfGHO/AU0d1fHDmfCYGJfta', '__Secure-1PSID': 'bQgdsbc_JRP81SvCAXXEZcip7rq1taCx3fv6xsgVlZsSrpyKS_HnlwZ_NTUxZ_CRXtkXxg.', '__Secure-1PSIDCC': 'ACA-OxO2dIB3uyeCw31moxOEVe3U9m9yPlFC7m1A7vY3bGbpFMF697rSyKHO6W3ZWR_tytjWiA', '__Secure-1PSIDTS': 'sidts-CjIB3e41hdoRGFx73QINnCx3bhPM1P2Bi_r91Y6vj2Tea0AyCKT5Te6qFQQr4jMYKB7oWBAA', '__Secure-3PAPISID': '2BRLvfTlO2VRfGHO/AU0d1fHDmfCYGJfta', '__Secure-3PSID': 'bQgdsbc_JRP81SvCAXXEZcip7rq1taCx3fv6xsgVlZsSrpyKc6IXsYreeJDH-e3Tk1S0kg.', '__Secure-3PSIDCC': 'ACA-OxNOhynzXOff6Nfz9lrLx8_KhAWQmJj7pDy8uiJN8RtoebI8X-Gy0zP94oohzLOCcVFVig', '__Secure-3PSIDTS': 'sidts-CjIB3e41hdoRGFx73QINnCx3bhPM1P2Bi_r91Y6vj2Tea0AyCKT5Te6qFQQr4jMYKB7oWBAA', 'AID': 'AJHaeXJV8_6QQoN8ms2RO37G3IV81ESI_siFBKjqvLJYTVevXaZRY5FTpno', 'TAID': 'AJHaeXJFicftgi7yGe6lPnxjTLB-V7b89w1uvAMBpmzpsI3p9UrHKZ_8lStM-9hVx5zBJDPQothQRtHjCCmUjUH6ERMpE_8lTvm-p3hCMsgGhh4Jjf_UT2Mqimgq7bTYI5-HUvsG9z91OA', '_ga_946NLLCQF5': 'GS1.1-2.1678292281.1.1.1678292415.0.0.0', 'SNID': 'ACchk07eo3IA_cTgZxoAWFoy06Rqe1jTIuFfw2fJpB-gplzHrYy1c2gSSZJZXXj3vQfhQio-PWr_7HsfxYYqAGqNux1UXObAfAI', 'G_ENABLED_IDPS': 'google', '_ga_H30R9PNQFN': 'GS1.1.1679998869.5.0.1679998869.0.0.0', 'ACCOUNT_CHOOSER': 'AFx_qI5PqDvTFMGZbFsjoGvcDBoplKIftWZwD2Mqp7t5Soykm4u-gYlogOMi3BDJS444mFomeAJgr0pBNzyx-ozoiaKXd4Tu9u9ua3kAovrELcho-2OcxsFOQQK14RNSgzkoaS6i5RCHWFvJJh4hhCyQ_lsEwvS63w', 'LSID': 'o.lens.google.com|s.IN|s.youtube:bQgdsbKF_BLQLOq3Umg3IgYKNl9YCa4T7bz1hX1owGV2Qi9xby1EHenCuHZ5B5zdZ_QosA.', 'LSOLH': '_SVI_EMCHgZqY3v0CGBAiP01BRURIZl9xb3RzVjRKb1hCcXA1Slp6OWlxVTRvYUw2bzVOMnNDT3Z3enNqTG9HZVZLemZkNEJwclVMR21jSQ_:27981548:1787', 'OTZ': '7197818_34_34__34_', 'SMSV': 'ADHTe-CFtPEqYFNrC_dsDMaUyo2GU9j8j8evMKlsiq1UjVWKTCOy_bB6AFC5WSrliCjmVrXIIpoNyVelTf3Lz6EpECuPjk-zADRw8q46vkRDvEBD9HNaKMQ', '__Host-1PLSID': 'o.lens.google.com|s.IN|s.youtube:bQgdsbKF_BLQLOq3Umg3IgYKNl9YCa4T7bz1hX1owGV2Qi9x8ZoLQioSL5DcV1tRu-M5Jw.', '__Host-3PLSID': 'o.lens.google.com|s.IN|s.youtube:bQgdsbKF_BLQLOq3Umg3IgYKNl9YCa4T7bz1hX1owGV2Qi9xODc7p1IsDJ2oWCiUKh_Miw.', '__Host-GAPS': '1:gfSUldRYBvwbjozNm24iOsG-mfVmO8AU9bMCqTr_os38J5PgIWFMg6an273XLzJ9qIVbtVbwgTJlisowKOk57hyrnde_yA:2oij8MwIcXhSURKr', 'user_id': '113341806006331731617', 'OSID': 'OwgdsRvdBsySNkJGy4jKnEizWtvHArqrMTu06sR4SabjGoox4YbgIen0WqOniwCtiabzPA.', '__Secure-OSID': 'OwgdsRvdBsySNkJGy4jKnEizWtvHArqrMTu06sR4SabjGoox2nLzv9nQJJXtMkmMFGKUmg.', '_ga_devsite': 'GA1.3.4037822407.1664088928', 'django_language': 'en', 'GMAIL_LF': '80000', 'DV': 'I40HF7Z4PfBYUHFnxQKTMX8_Fv3HrhgaJsH45ZPKQwIAABC-VjyYqfifpgAAAASIm0L1K13fNQAAAO4BBgAhOxlRDgAAAA'}
huggingface_token="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"

task_query=""
server="https://opengpt-4ik5.onrender.com/"
filen=""

installed_packages=['pandas', 'opencv-python', 'imageio', 'scikit-learn', 'spacy', 'bokeh', 'pytest', 'aiohttp', 'python-docx', 'nltk', 'textblob', 'beautifulsoup4', 'seaborn', 'plotly', 'tornado', 'matplotlib', 'xarray', 'librosa', 'gensim', 'soundfile', 'pytz', 'requests', 'scikit-image', 'xlrd', 'scipy', 'numpy', 'openpyxl', 'joblib', 'urllib3']
