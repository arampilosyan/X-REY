const input = document.getElementById("imageInput");
const preview = document.getElementById("previewImage");
const resultDiv = document.getElementById("result");

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
    return "";
}

// preview image
input.addEventListener("change", () => {
    const file = input.files[0];
    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
    }
});

// send image to backend
async function sendImage() {
    const file = input.files[0];

    if (!file) {
        alert("Please select an image");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);

    resultDiv.innerText = "⏳ Predicting...";

    try {
        const response = await fetch("/predict/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: formData,
            credentials: "same-origin"
        });

        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json")
            ? await response.json()
            : { error: await response.text() };

        if (!response.ok) {
            const errorText = data.error || "Prediction failed";
            const detailText = data.detail ? `\n${data.detail}` : "";
            resultDiv.innerText = `Error: ${errorText}${detailText}`;
            return;
        }
        resultDiv.innerText = `Result: ${data.prediction}`;
    } catch (error) {
        resultDiv.innerText = `❌ Error connecting to server: ${error.message}`;
        console.error(error);
    }
}