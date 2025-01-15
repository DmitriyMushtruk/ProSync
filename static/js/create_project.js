document.getElementById('createProjectForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);

    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.text().then(text => { throw new Error(text) });
        }
    })
    .then(data => {
        if (data.success) {
            let projectMainUrl = `/projects/main/${data.project_id}/`;
            window.location.href = projectMainUrl;
        } else {
            console.error('Failed to create project:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
});