# frontend/modulos/estilos_ud.py

CSS_INSTITUCIONAL = """
<style>
    :root {
        --ud-red: #8b0000;
        --ud-red-grad: linear-gradient(180deg, #8b0000 0%, #600000 100%);
        /* El verde con blanco que te gustó */
        --split-green-white: linear-gradient(to bottom, #00b09b 50%, #ffffff 50%);
        --text-dark: #333;
    }

    .section-title-custom {
        border-left: 6px solid var(--ud-red);
        padding-left: 1rem;
        margin: 1.5rem 0;
        color: #213142;
        text-transform: uppercase;
        font-weight: bold;
    }

    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 350px;
        perspective: 1000px;
        cursor: pointer;
    }

    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }

    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }

    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    /* FRENTE: Verde y Blanco */
    .flip-card-front {
        background: var(--split-green-white);
        color: var(--text-dark);
        border: 1px solid #ddd;
    }

    /* REVERSO: Vinotinto Puro */
    .flip-card-back {
        background: var(--ud-red-grad);
        color: white;
        transform: rotateY(180deg);
    }

    /* AVATAR RECTANGULAR (Ajustado para el .svg o iniciales) */
    .avatar-rect {
        width: 110px;
        height: 130px;
        border-radius: 12px;
        object-fit: cover;
        border: 4px solid white;
        background-color: #f8f9fa;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        font-weight: bold;
        color: #00b09b;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }

    .info-line {
        margin: 5px 0;
        font-size: 0.9rem;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        width: 100%;
        padding-bottom: 3px;
        text-align: left;
    }
</style>
"""