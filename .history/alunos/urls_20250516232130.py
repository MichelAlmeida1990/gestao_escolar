{% extends 'base.html' %}

{% block title %}{{ titulo }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>{{ titulo }}</h1>
        <a href="{% url 'alunos:aluno_list' %}" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i> Voltar
        </a>
    </div>
    
    <div class="card">
        <div class="card-body">
            <form method="post" enctype="multipart/form-data" novalidate>
                {% csrf_token %}
                
                <div class="row">
                    {% for field in form %}
                        <div class="col-md-6 mb-3">
                            <div class="form-group">
                                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                                {{ field }}
                                {% if field.errors %}
                                    <div class="invalid-feedback d-block">
                                        {{ field.errors }}
                                    </div>
                                {% endif %}
                                {% if field.help_text %}
                                    <small class="form-text text-muted">{{ field.help_text }}</small>
                                {% endif %}
                            </div>
                        </div>
                    {% endfor %}
                </div>
                
                <div class="d-flex justify-content-end mt-3">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Salvar
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
