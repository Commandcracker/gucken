from httpx import Client

headers = {
    "Host": "www.google.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/recaptcha/api2/bframe?hl=en&v=joHA60MeME-PNviL59xVH9zs&k=6Ldd07ogAAAAACktG1QNsMTcUWuwcwtkneCnPDOL",
    "Content-Type": "application/x-protobuffer",
    "Content-Length": "9540",
    "Origin": "https://www.google.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

payload = r"joHA60MeME-PNviL59xVH9zsù03AFcWeA4_lG8THQFptP9M3-wUwX8u_Z9cEiXqpwXgi6wEWWgLf6t9EtU1pi3-QgvcmPSZq9pVNkIzC0We04yZlabGNo905yLLwiyYZKFA4Ub192by2dWoaTO6nGJ7V3PY5_ospZh3b2JVZoA8k_6svjRi4NI9phtU01qnHCTZK3Z83kxXmO-lINZ-1WMYe7Th46NRLicl343j6XtwMtbQqQWH9iZ21qXyCQExxMO4paeZvC1RpJeswWCms302YsIGzO_7qTYYj6i0lSckZK8Tiaqo-90Rvp8selffkvkS5pZ70KwDJb8nd2NbLVZElB93bqeX7Ah24i9T3l-HVtc9raAonx7Tc3LnpcdMniWmP5ideIFx13CK0S0z84PWdr9Y5kf5Z0BHHc4N2-POBp8UpDdPQ9Xtot4FOTVoz0OhuiMlVSLSZm56b_PisgT-FpF9dtw8dWkG2O3MBMEqDFEMGOcsLtSBqRQM7_sVVbRFPAM2_F20dCLmtzPI9B2WchC5-KrVAz2C1xK8cYBcc3lybD8J12e0nu-7WbKGuDc70PZZkMUW4HYz478NWju2y5wRP8jqqN80OyDJOrtryFBtVqmBJDLrpGFJSbjkXpVc8uYlp9bKbfCt5AZvWHb6Mb9QWnomq0LncvMB0eP1_d3vztkXnyUVtX1PMQG1XuB3DQRf1DG6XgHirntjEqI50RArMjmoozDN3crEh7hTr-ywnFTwChzLNZNRBwm4md6J1Tn35Gwd4jXpWT4PPCyeZMIdsE31jj7CHVmTWcFiIeT5a-s3DIPBLXn6B8U3jdcqbhmrhCCPiMG_ladeyrbTCe0ys7Nqu17kNRBX38gj8Dv3Gx9jVBtBXkF1i6VT1hwdzkFnxQLSxYH_nCD6tSxZ5kwvEsg1oa9M1i3Ik-Q6lh-wkP69uzyn0AvP5ZCIpLg-MEaBOxCjvfyblM_irdudhgCHzuEPG-4nddTVW6aOsiE-zt7i61TQZ3ZlOZZ-_rLWnB-_3rIu0FKEjZDhTJo55-dx53f1DhYE0lNJu-bkciflFpuLxLDcFa5-qZB3JWEEMY0-ieFnfX7hru25M-5rK4jd2Ch5WFoSwTl3KcEmm7cRntxplRpAiscBpnlQ3IphaKVrWwgchYeGahNeOGdWPAZljXd8bylAsQxDG8eCXG_82Rwym560uSloCIMWFzrpwO2M4nQTCbkHUnwoEumQ6MNFeLS-Oh_Wvr9LXgA6Xg6foIp2z-YkLdEn7DCDraFBu1jUAS0qAuVSSpAkX6qYfg2Al98MKnjZBYaToHBMmVG8J3UjLW_NsmKvLnEnTKmnTVLhicHCiIlQKCHww6JogEY7BBhAxPIlalk0Mk7VSW-z2Br0INXogvHgfTUKfICqVXnA7JPFIPYM1Si_pDr-b5RclSQ37rkju3r1vddGO6P3gFiTdv92hcUawXlcFn2M8ZPK6sX-s2x8EEqD5J3bIUug-7weAj_AWy88wOikDVwWtSsN_dOA0ZpO1YW49RIypeHKsfzCd9bLE7s"á!rqigqK0KAAQeAfg6bQEHewKxWU4Jlxp4PoRnNKXodgbIIMfGXKnAzDVS8cTfqvx0l2b4Lf1gJFMFROusQCrv1jE_DrQA0qOqBjLreMQoFBP5mlNly-aEHXMf65zrB9JtwNXF6DiRqtrASD_Aelocv99FITYxB3rHge9axjAuiikZdjGSm9LniHBep51bsai_vg3RalDDPayqOA9p7vpuhwlpSL2E00EDqec_nWIFZnsin771ENMfeHS329lQziMvr3BTyvOmdMCouY826VNFL7-phQauSTZdbIw_NGMXxXvzgyi1PplePRFVSve2ttzACL0DMfZJ_CBLGvIK7Q0DFUlouxRLIv_M7rfqItPKsDqXrk4GLXdCO1UJD9Fxex1ElMg88AlG0OfHperhr5CWidswZCm1Bn5we8x6-rZkKHxAlSJAWcmAZA5Lmac2nCpXr8qOELzo3kN24ufhe-B6poDYpnUwZm_8Gun-z3S8mKh0G6Jto2bkqU4tvybg0-Qme7IU5bGoPdUbUJNM_-8a6ifU16YJN7bu4RJNm2pwl5bcJmzilq7-IzUnlXHeSSG3ZRdVaLEXuNLqpLktvHZxiGbhjqFQiz4AchVM7RJp3UdmMqCMlgrYRehahqi3w2eZ1HLkAVg0DSTkOYsOO46jx6N0pI7i4yph7gfKfO7SfUuQvJnIheOYlQyWGiC84Psc-KQlZ2Vt_wG_RCVg4JZFrdj42VkJ8T1c6O2GJrewk7CeY0rrI9Fjywc07bpodVKykpxNFSGHeCsw2r4UhF4-3QK7R2JupqXlkU7GOEL841O_c1vv1SXL1Ifkk-7wO6jT_oMYVsbOEamZtG1llB-kx9vn9crqZJEDGfAlsfJTmLVMWQ4Sw7UVS7Fus_gsj8g2FQUDHh0NMKlg5kHJiGXdjBzMiPRnqyCnzTFrtogNH189N_ucCAITU134e8xpEHD0pw2e3Nu1exKAm0D7YTC8Jd12hvXi2kmF_21_6n87Bk6OkWBCCZ1wnr1cDWKNvOBOHIsPgXxlZnPonbqJKfJtvS1MzhnwmC_BDaCF0uSXd1ESJ5KWvCoU-xcQzMAR41SUs3s-glpki8hJpfNI-rq2xhRFAky48_UQBGv6zqiPDHQ9zUswyJFxwPfBnZbLt0cMEsb8ICGjD5TlElWyJsh3fROqU4lYGXsIiplhpOkP4j9COyOlvnqXqc5eW_ELKo4FMeIzRCHt-A03GiCFeHcIuxwxOxxeXzfLgpmUgpKfCQn6yt8IU2IKpkjA0t_opOr5iwWu28DXoSsMqad9BQLbcQpiD942R_vnwLSa0PfycckxAO5lAp7tKlVtmi1K-kiteOd2bvCfVYer1Vdx3mwHbGjmJH1PcAnfAPF298GMZVfBPyJP1-elcpfHxT2eNw05NXv5F1JW6tbCwp8MuWTbq1VDFGPpgwnOPRO6U88lmLUx-lUsWxqTSaQP1dGQLnQfqkLC8BXTQsJy4y9FN1Cmyl_pXiobPAlC4m1GYnZzExbEsZ-5nsqcci1c_7vv5ZIGIzpbzJb5hLDDugm-HBl6rWUXOVAP6jyk3GJzQ4cHXNjMp6VwDaAH1uJOUBWzRhotxOeNiOCb10l1Glm_PSdLqmZJGfpsw0LjFofVimNiZPpTmdCZ_f7jWpaREkfJPPmCARU-L-ko-LpVmzzJ6mPVyb-nAaPOj-ntuUj2fmNu_fMSNndhFh6btcaV7NRrrAMqiQfXjyy7i9MuuTuUyyGM-73WBdZx5CsIDX84iCG0JbMBa5AlJQjQmMfaNbeg4M4YakjoMI8LKmAAIV93SlX34KK7rIZehOrG2A6Td4iuR_2x_uDJAucUM33z8EpyA5Gj2jgcjcQ7QRsJW1-d5lVcCm7J3inYPj90ujI3HKFG7ISnxGSYm_umSTfC5h8idTb6_yGzn9Qj4w7ZplcZV2mfAPirNkUNBRXpaEzOrdVHTq6WxZrq0AUBYQIl_9W6iXIc5_LCPcXt1BUJGbRoQ3oIDhv33HuDztSk4mVMk5owfH187BNO5wvSzun4YbTeHujhOyny9Yij0E8wjEAOfBDZdkC8IGSkqy-tCTC8Emdw_9n3L52Br7OeeawMA9wabiNyFYN6pwcYVJaqwCvsE5rgmiNMihwW4YX_kjoKysKtBaa9lp2sUSbLOQdJrp0NcU6XVtg0rDbnPinBAU7N2u7Wo74NgdoH0qQTdmay292AMwBNT_LNbIx6CKh9904kn1-RYdhYibedHPGi08M1tyf24Ijggz7Rpo2hQo3smG-Pkkd0m_-Alu9Yy-o19hQE3VbW12OrqNbnDf1gnGtvrgZddf9o0JLeTQM30fCmt-BkM0ouz9yYqAPPGBQSE4Akrv8Y7XzyC7zJrHhoPtI5sS-_yq0U1uOeG64eAr5PzViQ6J8pwUGgEctJ4puiIiUkyCCclqiBfzOBE04VoK4pB0Wt3GTt8LxDkqCN-VIn00gDlsbPgVyf_R9y1HUVWo02MAPzrqcWcMC9e-C8gM6rShhKMiFCdmqlvhFHUKoYGCsTUAd5-glsdpsta2Dj17CFWsq6P_ZaSW3HFrYgNftlSVRmsxozJHRkHdau8Zwy7hwCd0_tGm_ssWrx8xhc1nTay1lx_RbXX7yer70AF0gwbKakFinrMyVHEULea72JCixovDnwEPBHYqKMUHvVu2h4C4W2Ma5ZnB_0RAdqRZ3YTXdjcEMosJuiESsqL47HcbMKBtG9CIDS3l225hWVikDpTtg95f6M1A-a7ouK7Qn1EL3zpc7o-YnRa_Ob9VV2LNboeZx4YB-2N-zyY8JcbiCUz7yFeBLQtb7QS4dJhrMWoUWNCx82_GDOC19gfOhjFSFMLDC3YjyYLit59mUZMxlmsKrSUj8I-7xifK1s3ZJHb0uI-YVClyHX6m42V57S_NVoHaxxu9XJhQF8KU1nYW9RKPwHyh8qsa2L35fW5sUzRiMwNBjlG-QHmOfyC25dBq5LpsJ679-W2YsB7NOk-Ve89g-C85fxnUodJ1FDdnklM6loFmiCJD9nds6dJEBh8sBMt_yzg8kwb5XMhFfzI8MQrOFMhcP8scQTHRRdl42Ul9Mu0Ze509hRTPvusehAk-KMFfJ8OcKaNA0aVXI1qpPievYcPU9MNkO7YrxwTj05rOPbqM7LpCUEbOQPqul0HTHlERd0avYgMb4Ds8WBspx8j00fqJZWBVt6oAciT0KNmKMs14zjyxyO8fjGOqM_CKnJt1Rfgboha-iLq1yl7X1KeAt-KS_iHic3CXq8GONSUr6j-rbymOdRzYH5IG1jMVtVM6OdRLblAYCTUYiVrNQLrQGTgaBEMqVyO1ofmUf6y2_Ma-_S1zAHUGXbFp3MZGdeQTg-2bTSm_c9sWRof4nwsePbu-6URM6NkpBlq8AbBOowJMasm2GeTy_swCY7LSJo3mMDJsRpWZp9JvUr8N3EeO_SecBUpm627AFOTtsBYNYghbLZVRXCtrK3WIkro8p7eKnJu7aVdwfMAxTl78IM796frltzvoNzh3sPUPT1WvFMGD_r3U5fEopzsJMdLTKtObGjF2COhVuttt0x1veRmo4EQD_2EYbCZwlXWScp-3YS2_Ji5sV5rK4xO2m7sV3VwyTZ0UukiWIyAS2qWNZ50Og6PB2b1u6gkqRJheqI5ne3Io2zleI4qkY6*	8271120102fir(6Ldd07ogAAAAACktG1QNsMTcUWuwcwtkneCnPDOLÀ 0yDEBxXk2s7J2KudkYyfbmBUU2IxJxnk2_bt8NDP3q2jl5KhcGZaVWQ3KR0YKvnv497tvLKmobCDdWlkd0Y4LCs6CP7y7fzPwbWww5KEeCo50M9rNfyf-iFUP0pFNM-miOyDFfjfVtnUl5rNcOsWzYzvedmUOz4M-08tXG9GEhCPvxXg9wr5UGOVxSSWmplLtpmMFzMuPQwB9fED0sS4t8aVi396iVhOQj1MHxEFABLh18vG1aSajomYa11RAxMFOEsmEdCUBs10S4oZqL6N6W-6dlyYXonwg47B8_tV0eP_tpVzkxnNbE812Q_yeWD3mvmoMzHBM58V2PyCaWFDqsmAsA7RlAsx9dhO_myv8vYUaBZxCCcuNTQK6gjj132tX29iWIiffdTjZgEcLyodC-MB2Mx2plRkWtXJR-Ll2IcyxjUIKm1vpsHQ266phKd-chhL-gn8z2HY9_8F7OO62bCkTn4sPDJ1cI-LKkQvboHcP85RGArxZIOShZBvRmU8M9oJu8u-LfwWjaizupWYb45lWQMy4PDnLojD3uXw686hwJuPNWUXJxmpF4Zp4Jf-OgxzIq3cM6pgT2p5dGtWLUwnGsDworKlXJeuaSRy2iVPf0o8uB758GgOGfiL4qSHorGom6JlgH9e-Sja6t1cQ1cJZKqJpK-2kZBrimFU_y7c7ON2hZuyzdTf0sWQr6qKJFQGFglDreUACxH4-8bh3LxaijhIP3Y4GzZFODsx-RQS8oy8bn5xRBrZhDdSYWg_OhUwLw6o2IqajVOjRVx7hnF4f2JlWCs-FPQW7eGLu2l5bBbpdQhm6ejHxxJEr3ro8QraEWfXKiDUaz4IgCLxlFQudaxUHjEAKsYAtBr2MQfa2f076vjwDx4k-_bR7OvLZZWQo3JkWAoaDC8iRjv8IlH0V14FUB_GOWtCXWRzak0gQxoNt-eVpZib1XSTmqGUg1ZxbE_qGcvbzxV8b-3hO9N6KayTVlCkPmVBE_MtjJtF-WPjndUX-yKg1EcxpNwnMcA3Ktj0j4HlyIOV6TRjapELo0YMh6MRiOAi3PxfXrGoSq4o9AM58NhnLYCj6tl8X2Kp9JNeMYCSkckL82psz1atYTdKRYTGxhFAyras78NyBMhyZZjDarl8y8pJ3KMaoPdifYSXcnFQT1ZFQB76APPm2oCwYnJlnApBXG9ibUgjPjkYtubh8MO1qVtrXiGn1i1IU1I1KCs2KQ_27cTPvrGlT38tPTP2mmUvxnUJJ2rRxFemnZerqfx4auZY_56lgEt-fXR4Cm3ss9ZRk_uh6XgzPdU3o0mEM2MFfNO2SNROtr0smopdNA9uWPfCKdhP2q3co-qJZHsuoQfe4Wyr1rTsCxYk__r16Le-raCUPm4cLCJaFSOSgbAmwdzv6tW8v6adrJ9mjXxf-inb695N27rV3OfCvZi7koYsXA4eEQAN7QgTFhD3zu3EuGKSjZxvYVUHFwm9SAclmKPCzWBXvhkj635Nc25p4MxfVhy3mmVQ4AJExD6uwaCfYdFnz22o26ppZJeGecRPQozAc54ZaFZptLeemUwv9nU8e8nx1I_GrS-PodlH5xmpTB7tiQ96RUjrRo0Yk43hEA52ANPfLXQnKmIEc3ZJvDfKKJQS2dmD4x2818a5lNtecVDHUlXcfqa9tH9CONNmwYQzinn00xbR6ENapZwLegVkOrJESBbFrTwuzXgG-tFcI56Y759qVPAibmEzKumwBxJlqE8qiZQqvY2MAzVwrE7NoS-OCcy_hlDUFzJwuA8dzRQrajEv_xoE32q59G9h3UgnbgTb1sFlg8MlNE-CEgRL4jncX5JZo6OaZRRuyaS8Yx5FEw39BIL5zLTfvpVgJsaRSEryFSAGbeBXln2gu0KIr68xiUw_AoDf0tWUnBKlc_eK6ew6xsVoD1IVN3ZyQD9PQSCjjsHj_zLlc79qdMu_bjF712Ysx2piKN8KRZhHybkwC018c8tF9Re-RSwQBkEAW1pBTMdGgOOG5bxn8r5ggEaRoBNS4fzK1bj4d44Ie-cyXOwPBbSvDyGUO7bRNAsmbQQC7kEAgsFRMDqeEHseaYBvMrUYJ4qw1_q92PNezgDDLmYcwv5l688mFROm6nlYbuXc5_rJ3HAqehBi3YyrsrWwj251ZFgCMePz5oWYf2atWGtOgOtifYyXamVAX1o51Ae1xbiy4dEwP8XxDA5-AStq0hjLPz4sR0pE8O82rMwW-nWcFy50Y4qqFCwOSZBDJpkQFvXpOAbGGPxupVSLUp2ZJ6INjGu6NbAzfmjYZsJsoCddMJeXBgw_RjEsw1XNuDp97VQvNZkjusY8W3J1zFd66STLTrWL-uZVdFK5yMLqBQwW-gTL5uHBX489TUPDYd0vowzsCxIU-Abp7N_K0bSHjn1wZA497__ygTTSwdzn7tHEo765mTdnFSUYGkXQL-aJpQ-6sZh-_oGop55c6HLGNRwazbQUFkFEzt2Mq7K9tJtuiYRkAjHj8-Z16I7-ZWAi1kykL5qZB2td5TOTJZRrkvFQ26pIzAsehQvawjD_bq5Ao-493HPh-KfC0bzPsoWgn38ZSPsK_cxrbnoM30otD7_Z9OgrBlSsSqpoz_7tXNf-cWCnvhWwn7pNfBdhZMvW1Zknpq1ke05w9Nr-QKffWhFULp3YjCI2CKsavPSL6pWwjw3449cZ8FwyzZzUMrVQ40Y5KGO-eU-ngqkLi4ookB9NaQsSBZ-yzdTjwr2Qr6qKJFQGFgjQBqXgmBW009rhxLeWsayMKllwc1Yp2-vebfvwCeVk05Zk-HLpgHwHPRAvNjk0EvINC-uFtWd27gkoF4XY99cmBDA_HXgH7wV4pvHkb4qVhH96gXRHUjUwBw388-eNvW9_csV71uXQV7tltLuqjVxYHrV8J6G9O-6WpPP2ycyjj1V82_KNXRf55JOutbybmnGMi2sFNOb26X0S_klYOtZFQJq99OuG5Xz4Ny2FS2sFgGsG7XiPinivXnmIc35dPFtWNdADscG31_601G9GabQDBkhccqYkq5pmAQ8OadRLXp1ABx4pb8L-PTgCtfz3rknQBuZc1FsaIW-mmkS8XqFJFzLZ2RwaZPT76cj4OxZtJ4ttbGfaighnvh2Ic36pXJMdxaizZgzkCrnor6r9rP8OjdRnTmkT9xqtk6NBuLBaikRvKxmgG_6tT-9KxXxrqoVn721EywIdJC8SIOPq2c13p1VlWCbZ5S_W5TxLpp1g53sJQLtSpXx7BgT0PuHsx46BHOg61Xx_djmkR75IjA8RwUx-4g0bcekEDx4I-8rl4MBejjxMQwpErBpGT-8KESALAczr5sZgkI-ebWNXBfk4SxoMAwXo_-r52OPKwaCzlmUxS3cpJUQfGXB3yimD60YAvLr-SWiXCWxgIkHtH1aNEIMB7LPbfjybj12JZ2rNPMQmPVyEHwGr-5Kxv_92UNO6eXDLx1JI-A7lCJgKUZgWynkEtyZFkHd9rWOi_cEDoum4u3rRgA8aFN-O4WRvyro5BubE9PAC0ce7tsWUin4tbH9OQDc6HTAfLg0X_vXU58qZZbCTUnzjsu1j-9oKBRfm2Mx_vs2ckoWIb4JtfF9mTUQnNhjrt6rp29augM_CSihYV2Y1Kx7ODR_u4NfavdC_zq20n5Z1hGs6BXigPtnY80LluF8RzGhKenWEV0k9OEsaDAOy8gDTxbi_orWgs5KZgHtaaUwe6u2oV2aFZHOJxRu_Yh1Hwl5Aj3Jk7M7-rez_zsC3up2wn66NlH92VWRLGeY0m_41YF8iydiHke0D3zWwtCJtY-vJ-ajr-sm_srWYr5qpiJN6cVBjRhTgD4745-NqySiG9aVnz3GFfxb1JNQXJfTq3eDH2sXUt76lnH-OcUAPVnEdIwbBTAvlyTfqclCAM3KBUEY5PCM2ITATGgD72unMn2qZjQiK7lTTmq4NJ55twNs-rTvXojGbnopMZ19dpUeTCiDjdgXwQs3V08emiKOCwZQf_i3dHC798-bpzOPO3bzHrqWEl3pJFUtDCTEb6nH5B0ZM83tZiTh7illPQkUoPyo5GCMKAOPy1aRznqKEjGamHTfiUahO1rWr29bltKqeTF_XQcx4QvY4jzLFbJ_2kdgf3YSjsqGMk5Z9XFc2PSwjFr2w¢D51bGwsbnVsbCxbbnVsbCxudWxsLG51bGwsWzAsbnVsbCwwXSxbMCxudWxsLDBdLDBdXQÊW10"
with Client() as client:
    key = "6Ldd07ogAAAAACktG1QNsMTcUWuwcwtkneCnPDOL"
    url = f"https://www.google.com/recaptcha/api2/reload?k={key}"
    response = client.post(url, headers=headers, con)
    print(response.text)



#https://www.google.com/recaptcha/api2/payload/audio.mp3
#?p=06AFcWeA6MU83cnC4_cn6aKo5ZOUSfjDxPW8YsDVlpz-8GQIseze6PNlxnk9phN4uz3IdTV0DAq8AHVc07BfNaWodgcmqtyXymksumGbJ1ihBu8y1qMcPFmWVzVQOyAxLQsNytMo3amxhkjrknSYGc4A7rIHHJJpYczuwv5-Oep4rk1rukfcaaoCZsbETuXdAZduNUIkNU13ZIoN6UVwSIMQ8GtwEK78ssOA
#&k=6Ldd07ogAAAAACktG1QNsMTcUWuwcwtkneCnPDOL