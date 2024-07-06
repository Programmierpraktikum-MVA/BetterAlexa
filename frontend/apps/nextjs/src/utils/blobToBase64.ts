export const blobToBase64 = (audioBlob: Blob) =>
  new Promise<string>((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result as string;
      resolve(base64);
    };
    reader.readAsDataURL(audioBlob);
  });
