document.getElementById("signupForm").addEventListener("submit", async function(event) {
    event.preventDefault(); // 기본 폼 제출 방지

    // 폼 데이터 수집
    const name = document.getElementById("name").value;
    const birthdate = document.getElementById("date").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch('https://127.0.0.1:5000/membership', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: new URLSearchParams({
                'name': name,
                'birthdate': birthdate,
                'email': email,
                'password': password,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data.message); // 서버에서 반환된 메시지
        } else {
            console.error('회원가입 실패');
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
