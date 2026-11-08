-- ============================================================
-- Vedas DBMS (CSBB 204) - 04_seed.sql
-- Sample data: 4 Vedas, 12 Kandas, 16 Suktas, 10 Rishis, 10 Deities,
-- 42 Mantras (famous ones verbatim), 20 Translations, 50 Word_Meanings,
-- 5 Themes with tags, 3 App_Users.
-- Run as root:  mysql -u root -p --default-character-set=utf8mb4 < sql/04_seed.sql
-- Headline mantras: 1 = RV 1.1.1 (agnimile), 16 = RV 3.62.10 (Gayatri),
--                   18 = RV 7.59.12 (Tryambakam), 25 = RV 10.9.1 (apo hi stha)
-- Leftover rows on purpose (for the LEFT JOIN report): rishi Agastya and
-- deity Surya have no mantras yet.
-- ============================================================
USE vedas_db;

-- ---------- Vedas ----------
INSERT INTO Vedas (veda_id, veda_name) VALUES
(1, 'Rigveda'),
(2, 'Samaveda'),
(3, 'Yajurveda'),
(4, 'Atharvaveda');

-- ---------- Kandas ----------
INSERT INTO Kandas (kanda_id, veda_id, kanda_number) VALUES
(1,  1, 1),    -- Rigveda Mandala 1
(2,  1, 2),    -- Rigveda Mandala 2
(3,  1, 3),    -- Rigveda Mandala 3
(4,  1, 7),    -- Rigveda Mandala 7
(5,  1, 8),    -- Rigveda Mandala 8
(6,  1, 9),    -- Rigveda Mandala 9
(7,  1, 10),   -- Rigveda Mandala 10
(8,  2, 1),    -- Samaveda Purvarcika 1
(9,  3, 1),    -- Yajurveda Kanda 1
(10, 3, 40),   -- Yajurveda Kanda 40 (Isavasya)
(11, 4, 1),    -- Atharvaveda Kanda 1
(12, 4, 12);   -- Atharvaveda Kanda 12 (Bhumi sukta)

-- ---------- Suktas ----------
INSERT INTO Suktas (sukta_id, kanda_id, sukta_number) VALUES
(1,  1, 1),    -- RV 1.1   Agni
(2,  1, 2),    -- RV 1.2   Agni
(3,  1, 3),    -- RV 1.3   Agni
(4,  1, 48),   -- RV 1.48  Ushas
(5,  2, 23),   -- RV 2.23  Brihaspati
(6,  3, 62),   -- RV 3.62  Savitr
(7,  4, 59),   -- RV 7.59  Rudra
(8,  5, 2),    -- RV 8.2   Indra
(9,  6, 11),   -- RV 9.11  Soma Pavamana
(10, 7, 9),    -- RV 10.9  Waters
(11, 8, 1),    -- SV 1.1   Agni
(12, 8, 2),    -- SV 1.2
(13, 9, 1),    -- YV 1.1
(14, 10, 1),   -- YV 40.1  Isavasya
(15, 11, 1),   -- AV 1.1
(16, 12, 1);   -- AV 12.1  Bhumi

-- ---------- Rishis ----------
INSERT INTO Rishis (rishi_id, rishi_name) VALUES
(1,  'Madhuchchhandas'),
(2,  'Angiras'),
(3,  'Gritsamada'),
(4,  'Vishvamitra'),
(5,  'Vasistha'),
(6,  'Kanva'),
(7,  'Kashyapa'),
(8,  'Atri'),
(9,  'Bharadvaja'),
(10, 'Agastya');              -- no mantras yet (LEFT JOIN demo)

-- ---------- Deities ----------
INSERT INTO Deities (deity_id, deity_name) VALUES
(1,  'Agni'),
(2,  'Indra'),
(3,  'Surya'),                -- no mantras yet (LEFT JOIN demo)
(4,  'Savitr'),
(5,  'Ushas'),
(6,  'Varuna'),
(7,  'Soma'),
(8,  'Rudra'),
(9,  'Prithvi'),
(10, 'Brihaspati');

-- ---------- Mantras (42) ----------
INSERT INTO Mantras (mantra_id, sukta_id, rishi_id, deity_id, mantra_number, metre, sanskrit_text, iast_text) VALUES
-- RV 1.1 (Madhuchchhandas -> Agni)
(1,  1, 1, 1, 1, 'Gayatri',  'अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम्। होतारं रत्नधातमम्॥', 'agnimīḷe purohitaṃ yajñasya devaṃ ṛtvijam | hotāraṃ ratnadhātamam'),
(2,  1, 1, 1, 2, 'Gayatri',  'अग्निः पूर्वेभिरृषिभिरीड्यो नूतनैरुत। स देवान् अति प्रचिनोति॥', 'agniḥ pūrvebhir ṛṣibhir īḍyo nūtanair uta | sa devān ati prachinoti'),
(3,  1, 1, 1, 3, 'Gayatri',  'अग्निः सुमना हव्यं नो देवान् यजति शिक्षन्॥', 'agniḥ sumanā havyaṃ no devān yajati śikṣan'),
(4,  1, 1, 1, 4, 'Gayatri',  'अग्ने त्वं हव्यवाहनो देवान् वक्षि सुवीर्यम्॥', 'agne tvaṃ havyavāhano devān vakṣi suvīryam'),
-- RV 1.2 (Angiras -> Agni)
(5,  2, 2, 1, 1, 'Gayatri',  'वयं त्वा अग्ने हविषा मदन्तो हविष्कृतो वृणीमहे॥', 'vayaṃ tvā agne haviṣā madanto haviṣkṛto vṛṇīmahe'),
(6,  2, 2, 1, 2, 'Gayatri',  'अग्निर्देवानां मुखतः प्रथमो यज्ञस्य साधनः॥', 'agnir devānāṃ mukhataḥ prathamo yajñasya sādhanaḥ'),
(7,  2, 2, 1, 3, 'Gayatri',  'अग्ने पाहि शर्मणा त्वा गृणीमहे हविषा॥', 'agne pāhi śarmaṇā tvā gṛṇīmahe haviṣā'),
-- RV 1.3 (Angiras -> Agni)
(8,  3, 2, 1, 1, 'Gayatri',  'अग्ने दूतो देवानां हविर्देवो हव्यं नय॥', 'agne dūto devānāṃ havir devo havyaṃ naya'),
(9,  3, 2, 1, 2, 'Gayatri',  'स नः शर्मणा सुवीर्येणाग्ने रयिं दधातु॥', 'sa naḥ śarmaṇā suvīryeṇāgne rayaṃ dadhātu'),
-- RV 1.48 (Angiras -> Ushas)
(10, 4, 2, 5, 1, 'Gayatri', 'उषसो व्युष्टौ सत्या विभात्यरुणा विश्वतः॥', 'uṣaso vyuṣṭau satyā vibhāty aruṇā viśvataḥ'),
(11, 4, 2, 5, 2, 'Gayatri', 'सा न उषाः शर्म समृध्नातु विश्वतो दिशम्॥', 'sā na uṣaḥ śarma samṛdhnātu viśvato diśam'),
-- RV 2.23 (Gritsamada -> Brihaspati)
(12, 5, 3, 10, 1, 'Trishtubh', 'गणानां त्वा गणपतिं हवामहे कविं कवीनामुपमश्रवस्तमम्। ज्येष्ठराजं ब्रह्मणां ब्रह्मणस्पत आ नः शृण्वन्नूतिभिः सीद सादनम्॥', 'gaṇānāṃ tvā gaṇapatiṃ havāmahe kaviṃ kavīnām upamaśravastamam | jyeṣṭharājaṃ brahmaṇāṃ brahmaṇaspata ā naḥ śṛṇvann ūtibhiḥ sīda sādanam'),
(13, 5, 3, 10, 2, 'Trishtubh', 'ब्रह्मणस्पते पाहि नो गणस्य हविष्मतः॥', 'brahmaṇaspate pāhi no gaṇasya haviṣmataḥ'),
-- RV 3.62 (Vishvamitra -> Savitr)
(14, 6, 4, 4, 1, 'Trishtubh', 'सविता चित्रमुग्रो असुरो नो रयिं ददातु॥', 'savitā citram ugro asuro no rayaṃ dadātu'),
(15, 6, 4, 4, 9, 'Trishtubh', 'सवितुः प्रसवे दिवि सूर्यो गोपा व्यश्चरत्॥', 'savituḥ prasave divi sūryo gopā vyaścarat'),
(16, 6, 4, 4, 10, 'Gayatri', 'तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि। धियो यो नः प्रचोदयात्॥', 'tat savitur vareṇyaṃ bhargo devasya dhīmahi | dhiyo yo naḥ prachodayāt'),
-- RV 7.59 (Vasistha -> Rudra)
(17, 7, 5, 8, 1, 'Trishtubh', 'रुद्राय शर्मकृते तुभ्यं नमो अस्तु शिवतमाय॥', 'rudrāya śarmakṛte tubhyaṃ namo astu śivatamāya'),
(18, 7, 5, 8, 12, 'Anushtubh', 'त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्। उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात्॥', 'tryambakaṃ yajāmahe sugandhiṃ puṣṭivardhanam | urvārukam iva bandhanān mṛtyor mukṣīya māmṛtāt'),
-- RV 8.2 (Kanva -> Indra)
(19, 8, 6, 2, 1, 'Trishtubh', 'इन्द्रायेन्दो परि स्रव सुतो मदाय शचीपते॥', 'indrāyendo pari srava suto madāya śachīpate'),
(20, 8, 6, 2, 2, 'Trishtubh', 'इन्द्र शचीपते सुतस्य मदेन वृत्रं जहि॥', 'indra śachīpate sutosya madena vṛtraṃ jahi'),
(21, 8, 6, 2, 3, 'Trishtubh', 'वृत्रहा सोमपाः शतक्रतुर्देवेषु वाजिनां पतिः॥', 'vṛtrahā somapāḥ śatakratur deveṣu vājināṃ patiḥ'),
-- RV 9.11 (Kashyapa -> Soma Pavamana)
(22, 9, 7, 7, 1, 'Jagati', 'पवमानः सोमो अर्कैरिन्द्राय पातवे सुतः॥', 'pavamānaḥ somo arkair indrāya pātave sutaḥ'),
(23, 9, 7, 7, 2, 'Jagati', 'इन्दुरिन्द्रस्य पीतये शुक्रो वाजेषु गच्छति॥', 'indur indrasya pītaye śukro vājeṣu gacchati'),
(24, 9, 7, 7, 3, 'Jagati', 'त्वं सोम धारया सुतो देवान् यज्ञस्य साधनम्॥', 'tvaṃ soma dhārayā suto devān yajñasya sādhanam'),
-- RV 10.9 (Angiras -> Varuna, waters)
(25, 10, 2, 6, 1, 'Anushtubh', 'आपो हि ष्ठा मयोभुवस्ता न ऊर्जे दधातन। महे रणाय चक्षसे॥', 'āpo hi ṣṭhā mayobhuvastā na ūrje dadhātan | mahe raṇāya chakṣase'),
(26, 10, 2, 6, 2, 'Pankti', 'आपो अस्मान् मातरो अवन्तु शर्मणा विश्वतः॥', 'āpo asmān mātaro avantu śarmaṇā viśvataḥ'),
-- SV 1.1 (Angiras -> Agni)
(27, 11, 2, 1, 1, 'Gayatri', 'अग्निमायाहि देवेषु गातुमन्तं हवामहे॥', 'agnim āyāhi deveṣu gātumantaṃ havāmahe'),
(28, 11, 2, 1, 2, 'Gayatri', 'सम्राज्ज्योतिरुग्रो अग्निर्देवान् हव्यं नयतु॥', 'samrāj jyotir ugro agnir devān havyaṃ nayatu'),
(29, 11, 2, 1, 3, 'Gayatri', 'अग्ने नो रयिं देहि प्रजां च शर्म च दीर्घमायुः॥', 'agne no rayaṃ dehi prajāṃ ca śarma ca dīrgham āyuḥ'),
-- SV 1.2 (Kashyapa)
(30, 12, 7, 1, 1, 'Jagati', 'अ नो भद्राः क्रतवो यन्तु विश्वतोऽदब्धासो अपरीतास उद्भिदः। देवा नो यथा सदमिद् वृधे असन्नप्रायुवो रक्षितारो दिवे-दिवे॥', 'a no bhadrāḥ kratavo yantu viśvato.dabdhāso aparītāsa udbhidaḥ | devā no yathā sadam id vṛdhe asann aprāyuvo rakṣitāro dive-dive'),
(31, 12, 7, 1, 2, 'Jagati', 'सुमति नो देवा अस्य यज्ञस्य साधयन्तु विश्वतः॥', 'sumati no devā asya yajñasya sādhayantu viśvataḥ'),
-- YV 1.1 (Bharadvaja)
(32, 13, 9, 4, 1, 'Jagati', 'भद्रं कर्णेभिः शृणुयाम देवाः भद्रं पश्येमाक्षभिर्यजत्राः। स्थिरैरङ्गैस्तुष्टुवाग्ं सस्तनूभिर्व्यशेम देवहितं यदायुः॥', 'bhadraṃ karṇebhiḥ śṛṇuyāma devāḥ bhadraṃ paśyemākṣabhir yajatrāḥ | sthirair aṅgais tuṣṭuvāgaṃ sastanūbhir vyaśema devahitaṃ yad āyuḥ'),
(33, 13, 9, 1, 2, 'Anushtubh', 'असतो मा सद्गमय। तमसो मा ज्योतिर्गमय। मृत्योर्मा अमृतं गमय॥', 'asato mā sad gamaya | tamaso mā jyotir gamaya | mṛtyor mā amṛtaṃ gamaya'),
(34, 13, 9, 10, 3, 'Anushtubh', 'सह नाववतु। सह नौ भुनक्तु। सह वीर्यं करवावहै। तेजस्विनावधीतमस्तु मा विद्विषावहै॥', 'saha nāv avatu | saha nau bhunaktu | saha vīryaṃ karavāvahai | tejasvināv adhītam astu mā vidviṣāvahai'),
-- YV 40.1 Isavasya (Angiras)
(35, 14, 2, 8, 1, 'Anushtubh', 'ईशा वास्यमिदं सर्वं यत्किञ्च जगत्यां जगत्। तेन त्यक्तेन भुञ्जीथा मा गृधः कस्यस्विद्धनम्॥', 'īśā vāsyam idaṃ sarvaṃ yat kiñca jagatyāṃ jagat | tena tyaktena bhuñjīthā mā gṛdhaḥ kasya svid dhanam'),
(36, 14, 2, 1, 18, 'Anushtubh', 'अग्ने नय सुपथा राये अस्मान्विश्वानि देव वयुनानि विद्वान्। युयोध्यस्मज्जुहृराणमेनो भूयिष्ठां ते नमउक्तिं विधेम॥', 'agne naya supathā rāye asmān viśvāni deva vayunāni vidvān | yuyodhy asmaj juhurāṇam eno bhūyiṣṭhāṃ te nama uktiṃ vidhema'),
(37, 14, 2, 8, 15, 'Anushtubh', 'पूर्णमदः पूर्णमिदं पूर्णात्पूर्णमुदच्यते। पूर्णस्य पूर्णमादाय पूर्णमेवावशिष्यते॥', 'pūrṇam adaḥ pūrṇam idaṃ pūrṇāt pūrṇam udacyate | pūrṇasya pūrṇam ādāya pūrṇam evāvaśiṣyate'),
-- AV 1.1 (Atri -> Agni)
(38, 15, 8, 1, 6, 'Jagati', 'सत्यमेव जयते नानृतं सत्येन पन्था विततो देवयानः। येनाक्रमन्त्यृतयो ह्याप्तकामा यत्र तत् सत्यस्य परमं निधानम्॥', 'satyam eva jayate nānṛtaṃ satyena panthā vitato devayānaḥ | yenākramanty ṛtayo hy āptakāmā yatra tat satyasya paramaṃ nidhānam'),
(39, 15, 8, 1, 7, 'Trishtubh', 'यज्ञेन यज्ञमयजन्त देवास्तानि धर्माणि प्रथमान्यासन्॥', 'yajñena yajñam ayajanta devās tāni dharmāṇi prathamāny āsan'),
(40, 15, 8, 1, 8, 'Gayatri', 'अग्निः प्रथमो देवतानां यज्ञेषु हव्यवाहनः॥', 'agniḥ prathamo devatānāṃ yajñeṣu havyavāhanaḥ'),
-- AV 12.1 (Angiras -> Prithvi)
(41, 16, 2, 9, 1, 'Anushtubh', 'पृथ्वी शान्तिरन्तरिक्षं शान्तिर्द्यौः शान्तिरापः शान्तिरोषधयः शान्तिः॥', 'pṛthivī śāntir antarikṣaṃ śāntir dyauḥ śāntir āpaḥ śāntir oṣadhayaḥ śāntiḥ'),
(42, 16, 2, 9, 12, 'Pankti', 'माता भूमिः पुत्रोऽहं पृथिव्याः॥', 'mātā bhūmiḥ putro.ahaṃ pṛthivyāḥ');

-- ---------- Translations (20: 14 approved, 6 pending) ----------
INSERT INTO Translations (mantra_id, translator_name, text, status) VALUES
(1,  'Ralph T.H. Griffith',  'I laud Agni, the chosen Priest, God, minister of sacrifice, the hotar, giver of treasures.', 'approved'),
(1,  'H.H. Wilson',          'I praise Agni, the domestic priest, the divine ministrant of the rite, the invoker, bestower of wealth.', 'approved'),
(2,  'H.H. Wilson',          'Agni, worthy to be praised by ancient and modern seers, conducts the gods hither.', 'approved'),
(3,  'Swami Dayananda',      'Agni, of benevolent mind, duly presents our oblation to the gods.', 'approved'),
(8,  'K.F. Geldner',         'O Agni, messenger of the gods, god of the oblation, convey the offering.', 'approved'),
(12, 'H.H. Wilson',          'We invoke you, lord of hosts, the most celebrated poet of poets, foremost king, priest of priests.', 'approved'),
(14, 'K.F. Geldner',         'May Savitr, the wondrous mighty lord, bestow wealth upon us.', 'approved'),
(16, 'Ralph T.H. Griffith',  'May we attain that excellent glory of Savitr the God: so may he stimulate our prayers.', 'approved'),
(16, 'Swami Dayananda',      'We meditate on the adorable glory of the radiant Sun: may he inspire our intellect.', 'approved'),
(18, 'Ralph T.H. Griffith',  'We worship Tryambaka, the fragrant, the increaser of prosperity: as a ripe cucumber from its stalk, so may I be delivered from death, not from immortality.', 'approved'),
(19, 'K.F. Geldner',         'O drop, flow round for Indra, pressed-for, for the rapture of the mighty lord.', 'approved'),
(25, 'Ralph T.H. Griffith',  'Waters, you that are wholesome, come to strengthen us: bestow strength and radiance upon us.', 'approved'),
(32, 'Ralph T.H. Griffith',  'May we hear with our ears what is auspicious, O gods: may we see with our eyes what is auspicious, O worshipful ones.', 'approved'),
(42, 'H.H. Wilson',          'The earth is my mother, and I am the son of the earth.', 'approved'),
(5,  'Jamison-Brereton',     'We choose you, Agni, with oblation, rejoicing, made officiants by the oblation.', 'pending'),
(10, 'Jamison-Brereton',     'At the breaking of dawn the truthful reddish one shines everywhere.', 'pending'),
(17, 'Jamison-Brereton',     'Homage to Rudra, the maker of shelter, the most auspicious one.', 'pending'),
(28, 'Student-Project',      'The sovereign light, mighty Agni, shall lead the gods to the oblation.', 'pending'),
(33, 'Student-Project',      'From the unreal lead me to the real: from darkness lead me to light: from death lead me to immortality.', 'pending'),
(36, 'Swami Dayananda',      'O Agni, lead us on the good path to wealth, knowing all our ways: remove from us the deceitful sin.', 'pending');

-- ---------- Word_Meanings (50) ----------
INSERT INTO Word_Meanings (mantra_id, word_order, sanskrit_word, dhatu, english_meaning) VALUES
-- Mantra 1: RV 1.1.1
(1, 1, 'agnim',        NULL,   'Agni, fire god (accusative)'),
(1, 2, 'īḷe',          'īḷ-',  'I praise, I invoke (1st sg. middle)'),
(1, 3, 'purohitam',    'dhā-', 'priest placed in front (accusative)'),
(1, 4, 'yajñasya',     'yaj-', 'of the sacrifice (genitive)'),
(1, 5, 'devam',        'div-', 'god, the shining one (accusative)'),
(1, 6, 'ṛtvijam',      'vid-', 'priest knowing the right seasons (accusative)'),
(1, 7, 'hotāram',      'hu-',  'invoker at the sacrifice (accusative)'),
(1, 8, 'ratnadhātamam','dhā-', 'best bestower of treasures (accusative, superlative)'),
-- Mantra 16: Gayatri
(16, 1, 'tat',          NULL,      'that (neuter)'),
(16, 2, 'savituḥ',      'sū-',    'of the stimulator, of Savitr (genitive)'),
(16, 3, 'vareṇyam',     'vṛ-',    'most desirable, excellent (accusative)'),
(16, 4, 'bhargo',       'bhṛj-',  'radiance, effulgence (accusative)'),
(16, 5, 'devasya',      'div-',   'of the god (genitive)'),
(16, 6, 'dhīmahi',      'dhā-',   'may we hold in thought (1st pl. middle)'),
(16, 7, 'dhiyo',        'dhī-',   'thoughts, prayers (accusative plural)'),
(16, 8, 'prachodayāt',  'cud-',   'may he impel (3rd sg. causative optative)'),
-- Mantra 18: Tryambakam
(18, 1, 'tryambakam',   NULL,    'three-eyed one, Tryambaka (accusative)'),
(18, 2, 'yajāmahe',     'yaj-',  'we worship (1st pl. middle)'),
(18, 3, 'sugandhim',    NULL,    'fragrant (accusative)'),
(18, 4, 'puṣṭivardhanam','vṛdh-','increaser of prosperity (accusative)'),
(18, 5, 'urvārukam',    NULL,    'cucumber, mighty gourd (accusative)'),
(18, 6, 'iva',          NULL,    'like, as it were'),
(18, 7, 'bandhanāt',    'bandh-','from bondage, from the stalk (ablative)'),
(18, 8, 'mṛtyoḥ',       'mṛ-',   'of death (genitive)'),
(18, 9, 'mukṣīya',      'muc-',  'may I be released (1st sg. aorist subjunctive)'),
(18, 10, 'māmṛtāt',     'mṛ-',   'not from immortality (mā + amṛtāt, ablative)'),
-- Mantra 32: bhadram karnebhih
(32, 1, 'bhadram',     NULL,   'auspicious thing, welfare (accusative)'),
(32, 2, 'karṇebhiḥ',   'kṛ-',  'with the ears (instrumental plural)'),
(32, 3, 'śṛṇuyāma',    'śru-', 'may we hear (1st pl. optative)'),
(32, 4, 'devāḥ',       'div-', 'O gods (vocative)'),
(32, 5, 'paśyema',     'dṛś-', 'may we see (1st pl. injunctive)'),
(32, 6, 'akṣabhiḥ',    NULL,   'with the eyes (instrumental plural)'),
(32, 7, 'yajatrāḥ',    'yaj-', 'O worshipful ones (vocative)'),
(32, 8, 'vyaśema',     'aś-',  'may we enjoy (vi + aś, 1st pl. optative)'),
-- Mantra 33: asato ma
(33, 1, 'asataḥ',      'as-',  'from unreality, from non-being (ablative)'),
(33, 2, 'mā',          NULL,   'not (prohibitive particle)'),
(33, 3, 'sat',         'as-',  'reality, being (accusative)'),
(33, 4, 'gamaya',      'gam-', 'lead, cause to go (2nd sg. causative imperative)'),
(33, 5, 'tamasaḥ',     NULL,   'from darkness (ablative)'),
(33, 6, 'jyotih',      NULL,   'light (accusative)'),
-- Mantra 25: apo hi stha
(25, 1, 'āpaḥ',        'ap-',  'O waters (vocative)'),
(25, 2, 'hi',          NULL,   'indeed (particle)'),
(25, 3, 'ṣṭhā',        'sthā-','stand, stay (2nd pl. imperative)'),
(25, 4, 'mayobhuvaḥ',  'bhū-', 'bliss-bestowing (vocative)'),
(25, 5, 'ūrje',        NULL,   'for strength, for nourishment (dative)'),
(25, 6, 'dadhātan',    'dhā-', 'give, bestow (2nd pl. imperative)'),
-- Mantra 42: mata bhumih
(42, 1, 'mātā',        NULL,   'mother (nominative)'),
(42, 2, 'bhūmiḥ',      'bhū-', 'the earth (nominative)'),
(42, 3, 'putraḥ',      NULL,   'son (nominative)'),
(42, 4, 'pṛthivyāḥ',   'prath-','of the broad one, of the earth (genitive)');

-- ---------- Themes ----------
INSERT INTO Themes (theme_id, theme_name) VALUES
(1, 'fire'),
(2, 'dawn'),
(3, 'rain'),
(4, 'knowledge'),
(5, 'prosperity');

-- ---------- Theme tags ----------
INSERT INTO Mantra_Themes (mantra_id, theme_id) VALUES
(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(27,1),(28,1),(29,1),(36,1),(40,1),
(10,2),(11,2),
(25,3),(26,3),
(16,4),(32,4),(34,4),(38,4),
(12,5),(24,5),(37,5);

-- ---------- App users ----------
INSERT INTO App_Users (user_id, username, role) VALUES
(1, 'aarav',   'student'),
(2, 'meera',   'scholar'),
(3, 'devraj',  'editor');

-- ---------- Bookmarks ----------
INSERT INTO Bookmarks (user_id, mantra_id) VALUES
(1, 1), (1, 16), (1, 18), (3, 12);
