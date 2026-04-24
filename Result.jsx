import React, { useState, useEffect } from "react";
import styled from "styled-components";
import {
  FaCheckCircle,
  FaExclamationTriangle,
  FaMapMarkedAlt,
  FaLanguage, // Added icon for the dropdown
} from "react-icons/fa";

/* ---------- styles ---------- */

const Wrapper = styled.div`
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 2rem 1rem;
`;

const ResultCard = styled.div`
  background: var(--white);
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0px 8px 26px rgba(0,0,0,0.12);
  width: 100%;
  max-width: 700px;
  text-align: center;
`;

// NEW: Styles for the Language Selector area
const LangSelectorWrapper = styled.div`
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.5rem;
`;

const Select = styled.select`
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--primary);
  background: white;
  color: var(--primary);
  font-weight: 500;
  cursor: pointer;
  outline: none;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ImageRow = styled.div`
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
`;

const ImageBox = styled.div`
  text-align: center;
`;

const ImagePreview = styled.img`
  width: 260px;
  height: 260px;
  object-fit: cover;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.15);
`;

const Caption = styled.p`
  margin-top: 0.5rem;
  font-weight: 500;
  color: #555;
`;

const Title = styled.h2`
  font-size: 1.8rem;
  color: ${(props) =>
    props.$isHealthy ? "var(--primary)" : "#d9534f"};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-transform: capitalize;
`;

const Section = styled.div`
  width: 100%;
  text-align: left;
  margin-top: 1.2rem;
`;

const SectionTitle = styled.h3`
  color: var(--primary);
  border-bottom: 2px solid var(--secondary);
  margin-bottom: 0.8rem;
`;

const List = styled.ul`
  list-style: none;
  padding: 0;
`;

const ListItem = styled.li`
  background: #e9f7ef;
  margin-bottom: 0.6rem;
  padding: 0.8rem;
  border-radius: 10px;
  border-left: 5px solid var(--accent);
`;

const ButtonRow = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
`;

const Button = styled.button`
  padding: 11px 26px;
  border-radius: 50px;
  background: var(--primary);
  color: white;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 6px;
  border: none;
  cursor: pointer;

  &:hover {
    background: var(--secondary);
  }
`;

const SecondaryButton = styled(Button)`
  background: #777;
`;

/* ---------- component ---------- */

function Result({ result, reset, detectDefects }) {
  // --- STATE FOR TRANSLATION ---
  const [translatedTitle, setTranslatedTitle] = useState(result.deficiency);
  const [translatedSymptoms, setTranslatedSymptoms] = useState(result.organic_remedy);
  const [isTranslating, setIsTranslating] = useState(false);

  // Sync state if new results come in from a fresh upload
  useEffect(() => {
    setTranslatedTitle(result.deficiency);
    setTranslatedSymptoms(result.organic_remedy);
  }, [result]);

  const isHealthy = result.deficiency.toLowerCase().includes("healthy");

  // --- TRANSLATION HANDLER ---
  const handleTranslate = async (e) => {
    const lang = e.target.value;

    if (lang === "en") {
      setTranslatedTitle(result.deficiency);
      setTranslatedSymptoms(result.organic_remedy);
      return;
    }

    setIsTranslating(true);
    try {
      // 1. Translate the Title
      const titleRes = await fetch("http://localhost:8000/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: result.deficiency, target_lang: lang }),
      });
      const titleData = await titleRes.json();
      setTranslatedTitle(titleData.translated_text);

      // 2. Translate the Symptoms list
      const translatedList = await Promise.all(
        result.organic_remedy.map(async (text) => {
          const res = await fetch("http://localhost:8000/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, target_lang: lang }),
          });
          const data = await res.json();
          return data.translated_text;
        })
      );
      setTranslatedSymptoms(translatedList);
    } catch (err) {
      console.error("Translation Error:", err);
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <Wrapper>
      <ResultCard>
        {/* LANGUAGE DROPDOWN */}
        <LangSelectorWrapper>
          <FaLanguage size={20} color="var(--primary)" />
          <Select onChange={handleTranslate} disabled={isTranslating}>
            <option value="en">English</option>
            <option value="hi">Hindi (हिंदी)</option>
            <option value="te">Telugu (తెలుగు)</option>
            <option value="kn">Kannada (ಕನ್ನಡ)</option>
            <option value="es">Spanish (Español)</option>
          </Select>
        </LangSelectorWrapper>

        {/* IMAGES */}
        <ImageRow>
          <ImageBox>
            <ImagePreview src={result.previewUrl} />
            <Caption>Original Image</Caption>
          </ImageBox>

          {result.boxedImage && (
            <ImageBox>
              <ImagePreview src={result.boxedImage} />
              <Caption>Defected Regions</Caption>
            </ImageBox>
          )}
        </ImageRow>

        {/* TITLE */}
        <Title $isHealthy={isHealthy}>
          {isHealthy ? <FaCheckCircle /> : <FaExclamationTriangle />}
          {isTranslating ? "Translating..." : translatedTitle.replace("-", " ")}
        </Title>

        {/* REMEDIES / SYMPTOMS */}
        <Section>
          <SectionTitle>Symptoms</SectionTitle>
          <List>
            {isTranslating ? (
              <ListItem>Updating language...</ListItem>
            ) : (
              translatedSymptoms?.map((item, i) => (
                <ListItem key={i}>{item}</ListItem>
              ))
            )}
          </List>
        </Section>

        {/* BUTTONS */}
        <ButtonRow>
          {/* UPDATED: Only show the detection button if the leaf is NOT healthy */}
          {!result.boxedImage && !isHealthy && (
            <Button onClick={detectDefects}>
              <FaMapMarkedAlt />
              Show Defected Areas
            </Button>
          )}

          <SecondaryButton onClick={reset}>
            Analyze Another
          </SecondaryButton>
        </ButtonRow>
      </ResultCard>
    </Wrapper>
  );
}

export default Result;